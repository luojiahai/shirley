import os
import pathlib
import tempfile
from abc import ABC
from dataclasses import dataclass


@dataclass
class ClientOptions:
    local: str


class Client(ABC):

    def __init__(self, options: ClientOptions) -> None:
        self._options = options
        self._tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(pathlib.Path(tempfile.gettempdir()) / 'gradio')


    @property
    def local(self) -> bool:
        return self._options.local


    @property
    def tempdir(self) -> str:
        return self._tempdir
