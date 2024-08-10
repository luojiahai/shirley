from typing import Callable


class PickleableGenerator:

    def __init__(self, fn: Callable, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.generator = fn(*args, **kwargs)
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            value = next(self.generator)
            self.index += 1
            return value
        except StopIteration:
            raise

    def __getstate__(self):
        return (self.fn, self.args, self.kwargs, self.index)

    def __setstate__(self, state):
        self.fn, self.args, self.kwargs, self.index = state
        self.generator = self.fn(*self.args, **self.kwargs)
        for _ in range(self.index):
            next(self.generator)
