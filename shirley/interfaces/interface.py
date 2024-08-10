from abc import ABC, abstractmethod


class Interface(ABC):

    def __init__(self, *args, **kwargs) -> None:
        pass


    @abstractmethod
    def _make_components(self, *args, **kwargs) -> None:
        raise NotImplementedError()
