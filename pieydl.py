# Entry point
# Imports
import os
import sys

# Custom Modules
from modules.whichos.whichos import whichos
from modules.logger.logger import custom_logger
from modules.ytdlp.ytdlp import (
    is_file_downloaded_properly,
    is_ytdlp_present,
    is_ytdlp_upto_date,
)
from modules.download.download import download_atomically, download_file_parallelly


def make_appdata_filestructure(program_name: str) -> str:
    try:
        appdata_dir: str | None = os.getenv("appdata")
        if appdata_dir is None:
            critical("Could not get AppData. Exiting program...")
            sys.exit(1)

        pieydl_appdata_dir = os.path.join(appdata_dir, program_name)

        info(f"Making {program_name} directory in {appdata_dir}")
        os.makedirs(pieydl_appdata_dir, exist_ok=True)
        info("Successfully made appdata filestructure!")

        return pieydl_appdata_dir

    except Exception as err:
        errmsg = f"`make_appdata_filestructure` failed: {err}. Exiting..."
        critical(errmsg)
        sys.exit(1)


def main() -> None:
    __program_name__ = "pieydl"
    __version__ = "1.0.0"
    __operating_system__ = whichos()
    info(f"{__program_name__} version {__version__} has started executing")
    info(f"Running on OS: {__operating_system__}")

    info("Making appdata filestructure")
    pieydl_appdata_dir_path: str = make_appdata_filestructure(
        program_name=__program_name__
    )
    info(f"Successfully created appdata folder: {pieydl_appdata_dir_path}")

    info("Downloading yt-dlp binary for you")
    ytdlp_binary_fp = os.path.join(pieydl_appdata_dir_path, "yt-dlp.exe")
    download_file_parallelly(fp=ytdlp_binary_fp, url=ytdlp_binary_url)
    is_download_valid: bool = is_file_downloaded_properly(
        fp=ytdlp_binary_fp, url=ytdlp_binary_url
    )

    pass


if __name__ == "__main__":
    debug, info, error, critical = custom_logger()
    ytdlp_binary_url: str = (
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    )
    main()
