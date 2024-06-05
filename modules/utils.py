import os
import itertools
from typing import Any, Callable, List, TypeVar

T = TypeVar('T')

def flatmap(callback: Callable[[Any], List[T]], iterable: List[Any]) -> List[T]:
    return list(itertools.chain.from_iterable(map(callback, iterable)))

def getpath(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))

def read(path: str) -> str:
    with open(path, 'r') as file:
        return file.read()
