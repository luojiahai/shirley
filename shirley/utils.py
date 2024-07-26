import os
from PIL import Image


def getpath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def isimage(file_path: str) -> bool:
    try:
        with Image.open(file_path) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
