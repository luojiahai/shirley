import os
import pathlib
import tempfile
from abc import ABC, abstractmethod


class Component(ABC):

    def __init__(self) -> None:
        self._tempdir = os.environ.get('GRADIO_TEMP_DIR') or str(pathlib.Path(tempfile.gettempdir()) / 'gradio')


    @property
    def tempdir(self) -> str:
        return self._tempdir


    @abstractmethod
    def make_components(self, *args, **kwargs) -> None:
        raise NotImplementedError()
