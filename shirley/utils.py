import os


def getpath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))
