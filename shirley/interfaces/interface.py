from abc import ABC, abstractmethod
from shirley.options import InterfaceOptions


class Interface(ABC):

    def __init__(self, options: InterfaceOptions = InterfaceOptions()) -> None:
        pass


    @abstractmethod
    def _make_components(self, options: InterfaceOptions) -> None:
        raise NotImplementedError()
