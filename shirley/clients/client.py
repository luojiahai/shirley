import os
import pathlib
import tempfile
from abc import ABC


class Client(ABC):

    def __init__(self, local: bool) -> None:
        self._local = local
        self._tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(pathlib.Path(tempfile.gettempdir()) / 'gradio')


    @property
    def local(self) -> bool:
        return self._local


    @property
    def tempdir(self) -> str:
        return self._tempdir
