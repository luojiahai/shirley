import gradio as gr
import logging
import sys
from .interface import Interface


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Footer(Interface):
    
    def __init__(self) -> None:
        super().__init__()


    def make_components(self, *args, **kwargs) -> None:
        gr.Markdown(
            '<font size=2>Note: We strongly advise users not to knowingly generate or allow others to knowingly \
            generate harmful content, including hate speech, violence, pornography, deception, etc. \
            (注：我们强烈建议，用户不应传播及不应允许他人传播以下内容，包括但不限于仇恨言论、暴力、色情、欺诈相关的有害信息。)'
        )
