import gradio as gr
import logging
import sys
from .interface import Interface
from shirley.options import FooterInterfaceOptions


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Footer(Interface):
    
    def __init__(self, options: FooterInterfaceOptions = FooterInterfaceOptions()) -> None:
        super().__init__(options)

        self._make_components(options=options)


    def _make_components(self, options: FooterInterfaceOptions) -> None:
        pass
