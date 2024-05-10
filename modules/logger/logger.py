from datetime import datetime


def custom_logger():
    """
    Higher order function that returns other functions for logging purpose.

    """

    def log(message: str, level: str) -> None:
        ts: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{ts}] --> [{level}] --> {message}"
        print(msg)

    def debug(message: str) -> None:
        log(message, "DEBUG")

    def info(message: str) -> None:
        log(message, "INFO")

    def error(message: str) -> None:
        log(message, "ERROR")

    def critical(message: str) -> None:
        log(message, "CRITICAL")

    return debug, info, error, critical
