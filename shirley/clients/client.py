import os
import pathlib
import tempfile
from abc import ABC
from shirley.options import ClientOptions
from typing import Type


class Client(ABC):

    def __init__(self, options: Type[ClientOptions] = ClientOptions()) -> None:
        self._tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(pathlib.Path(tempfile.gettempdir()) / 'gradio')


    @property
    def tempdir(self) -> str:
        return self._tempdir
