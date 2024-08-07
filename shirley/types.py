import numpy as np
import pathlib
from gradio.components import Component
from gradio.components.multimodal_textbox import MultimodalValue
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from typing import Iterator, List, Sequence, Tuple


QwenQuery = str
QwenHistory = HistoryType

GradioComponents = Component | Sequence[Component] | None


# Components
ChatbotTuplesInput = List[List[str | Tuple | None]]
ChatbotTuplesOutput = List[List | Tuple]

ChatHistoryInput = List[Tuple]
ChatHistoryOutput = List[Tuple]

MultimodalTextboxInput = MultimodalValue
MultimodalTextboxOutput = MultimodalValue

TextboxInput = str | None
TextboxOutput = str | None

SpeechTextInput = str
SpeechTextOutput = str

AudioInput = str | Tuple[int, np.ndarray] | None
AudioOutput = str | pathlib.Path | bytes | Tuple[int, np.ndarray] | None


# Chat
ChatComponentOutput = ChatbotTuplesOutput | ChatHistoryOutput | MultimodalTextboxOutput
ChatComponentsOutput = ChatComponentOutput | Sequence[ChatComponentOutput] | Iterator[Sequence[ChatComponentOutput]] | None


# Speech
SpeechComponentOutput = TextboxOutput | AudioOutput
SpeechComponentsOutput = SpeechComponentOutput | Sequence[SpeechComponentOutput] | None
