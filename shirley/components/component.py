from abc import ABC, abstractmethod


class Component(ABC):

    def __init__(self) -> None:
        pass


    @abstractmethod
    def make_components(self, *args, **kwargs) -> None:
        raise NotImplementedError()
