import platform


def whichos() -> str:
    return platform.system() if platform.system() is not None else "Unknown"
