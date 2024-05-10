import math
import os
import tempfile
import threading
from threading import Thread
from typing import List

import requests
from requests import Response

from modules.logger.logger import custom_logger

debug, info, error, critical = custom_logger()


def download_atomically(
    fp: str,  # Path where the downloaded file will be stored
    url: str,  # URL from which to download the file
    fmode: str = "wb",  # File mode for opening the temporary file
    chunk_size: int = 8192,  # Chunk size for downloading the file
) -> bool:
    """
    Get a file from the internet in an atomic fashion.

    Parameters:
    - file_path (str): Path where the downloaded file will be stored.
    - url_to_dl (str): URL from which to download the file.
    - fmode (str, optional): File mode for opening the temporary file. Default is "wb".
    - dl_chunk_size (int, optional): Chunk size for downloading the file. Default is 8192 bytes.

    Returns:
    - bool: True if the update is successful, False otherwise.

    Notes:
    - This function downloads a file from the given URL to a temporary file and then atomically replaces the existing file with the downloaded one.
    - Since the file is atomically downloaded, the file is either updated successfully or if the update fails for some reason, the old file is untouched and will be kept as is.
    - If an error occurs during downloading or updating the file, appropriate error messages are logged, and any temporary files are cleaned up.
    """

    # Create a temporary file to download the new content
    temp_file_path = None

    try:
        # Create a temporary file
        temp_file_descriptor, temp_file_path = tempfile.mkstemp()

        # Open the temporary file
        with os.fdopen(fd=temp_file_descriptor, mode=fmode) as temp_file:
            # Make a GET request to download the file content
            response: Response = requests.get(url=url, stream=True, timeout=(10, 10))
            response.raise_for_status()

            # Write the downloaded content to the temporary file in chunks
            for chunk in response.iter_content(chunk_size=chunk_size):
                temp_file.write(chunk)

        # Replace the existing file with the downloaded file atomically
        os.replace(temp_file_path, fp)

        # Log a success message
        info(f"`{fp}` downloaded successfully!")
        return True

    except (requests.RequestException, OSError) as e:
        error(f"Failed to download file at `{fp}`: {e}")
        return False
    finally:
        # Perform cleanup after update (remove any remaining temporary files)
        if temp_file_path and os.path.exists(temp_file_path):
            info(f"Performing post update cleanup for `{fp}`")
            os.remove(temp_file_path)


def download_chunk(fp: str, url: str, start_byte: int, end_byte: int) -> None:
    try:
        # info(f"(download_chunk) downloading from {start_byte} to {end_byte}")
        headers = {"Range": f"bytes={start_byte}-{end_byte}"}
        response: Response = requests.get(
            url=url, headers=headers, stream=True, timeout=(10, 10)
        )
        if response.status_code // 100 != 2:
            error(f"(download_chunk) Request failed: {response.status_code}")
            return
        with open(fp, "r+b") as f:
            f.seek(start_byte)
            f.write(response.content)
        return
    except Exception as err:
        error(f"(download_chunk) failed: {err}")
        # err.add_note("Function: download_chunk")
        # err.add_note(f"Error: {err}")
        raise


def download_file_parallelly(
    fp: str,
    url: str,
    chunk_size: int = 1024 * 1024 * 4,  # ==> 4 MB
) -> bool:
    num_chunks: int
    total_file_size: int
    start_byte: int
    end_byte: int
    threads: List[Thread] = []
    try:
        response: Response = requests.head(url)
        total_file_size = int(response.headers.get("Content-Length", 0))
        info(f"Total size: {total_file_size} bytes")
        # Dynamic chunking
        if total_file_size < chunk_size:
            num_chunks = 1
        else:
            num_chunks = math.ceil(total_file_size / chunk_size)
        info(
            f"Number of chunks to download file of size `{total_file_size}` = {num_chunks}"
        )

        with open(fp, "wb") as f:
            f.write(b"\0" * total_file_size)
            for i in range(num_chunks):
                start_byte = i * chunk_size
                end_byte = (
                    start_byte + chunk_size - 1
                    if i < num_chunks - 1
                    else total_file_size - 1
                )
                thread: Thread = Thread(
                    target=download_chunk,
                    args=(fp, url, start_byte, end_byte),
                )
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()
            # info(f"(download_file_parallelly) Download complete for: `{fp}`")
            return True
    except Exception as err:
        error(f"(download_file_parallelly) failed: {err}")
        # err.add_note("Function: download_file_parallelly")
        # err.add_note(f"Error: {err}")
        raise
