from typing import Dict, Any
import os
import json
from requests import Response, head
from modules.logger.logger import custom_logger

debug, info, error, critical = custom_logger()


def is_ytdlp_present() -> bool:
    pass


def is_ytdlp_upto_date() -> bool:
    # TODO: use last modified from header
    pass


def is_file_downloaded_properly(fp: str, url: str) -> bool:
    try:
        # Check if local file even exists
        if not os.path.exists(fp):
            errmsg = f"File does not exist: {fp}"
            critical(errmsg)
            return False
        # Match content length of downloaded file and online file
        response: Response = head(url=url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to send request to yt-dlp. Status Code: {response.status_code}"
            )
        response_headers: Dict[str, Any] = response.headers
        info(f"Type of response headers: {type(response_headers)}")
        info(f"Headers: {response_headers}")
        remote_content_length: int = response_headers.get("Content-Length", -1)
        if remote_content_length < 0:
            errmsg = (
                "Something went wrong. Could not get content length of yt-dlp binary"
            )
            error(errmsg)
            return False

        local_content_length: int = 0
        local_content_length = os.path.getsize(fp)

        if local_content_length != remote_content_length:
            errmsg = f"Local filesize and remote filesize do not match\nLocal Filesize: {local_content_length}\nRemote Filesize: {remote_content_length}"
            error(errmsg)
            return False

        info("Local and remote filesizes match.")
        info(f"Local Filesize: {local_content_length}")
        info(f"Remote Filesize: {remote_content_length}")

        return True
    except Exception as err:
        errmsg = f"`is_file_downloaded_properly` failed: {err}"
        raise Exception(errmsg)
