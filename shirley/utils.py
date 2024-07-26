import os


def getpath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

def read(path: str) -> str:
    with open(path, 'r') as file:
        return file.read()
