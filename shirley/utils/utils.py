import os
from PIL import Image


def getpath(filepath: str) -> str:
    return os.path.abspath(os.path.expanduser(filepath))


def isimage(filepath: str) -> bool:
    try:
        with Image.open(filepath) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
