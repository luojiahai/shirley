import gradio as gr
import logging
import sys
from .interface import Interface


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Footer(Interface):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

        self._make_components(*args, **kwargs)


    def _make_components(self, *args, **kwargs) -> None:
        pass
