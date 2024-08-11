from abc import ABC, abstractmethod
from shirley.options import InterfaceOptions
from typing import Type


class Interface(ABC):

    def __init__(self, options: Type[InterfaceOptions] = InterfaceOptions()) -> None:
        pass


    @abstractmethod
    def _make_components(self, options: InterfaceOptions) -> None:
        raise NotImplementedError()
