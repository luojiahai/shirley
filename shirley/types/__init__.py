import gradio as gr
import numpy as np
import pathlib
from gradio.components.multimodal_textbox import MultimodalValue
from typing import List, Sequence, Tuple


QwenQuery = str
QwenHistory = List[Tuple[str, str]]

GradioComponents = gr.components.Component | Sequence[gr.components.Component] | None

DropdownInput = str | int | float | List[str | int | float] | List[int | None] | None
DropdownOutput = str | int | float | List[str | int | float] | None

ChatbotTuplesInput = List[List[str | Tuple[str, str] | gr.components.Component | None]] | None
ChatbotTuplesOutput = List[List[str | Tuple[str] | Tuple[str, str] | None] | Tuple] | None

MultimodalTextboxInput = MultimodalValue | None
MultimodalTextboxOutput = MultimodalValue | None

TextboxInput = str | None
TextboxOutput = str | None

AudioInput = str | Tuple[int, np.ndarray] | None
AudioOutput = str | pathlib.Path | bytes | Tuple[int, np.ndarray] | None
