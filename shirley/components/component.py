from abc import ABC, abstractmethod


class Component(ABC):

    @abstractmethod
    def make_components(self, *args, **kwargs) -> None:
        raise NotImplementedError()
