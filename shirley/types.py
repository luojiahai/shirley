import numpy as np
import pathlib
from gradio.components import Component
from gradio.components.multimodal_textbox import MultimodalValue
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from typing import Iterator, List, Sequence, Tuple


QwenQuery = str
QwenHistory = HistoryType

GradioComponents = Component | Sequence[Component] | None

DropdownInput = str | int | float | List[str | int | float] | List[int | None] | None
DropdownOutput = str | int | float | List[str | int | float] | None

ChatbotTuplesInput = List[List[str | Tuple[str, str] | Component | None]] | None
ChatbotTuplesOutput = List[List[str | Tuple[str] | Tuple[str, str] | None] | Tuple] | None

MultimodalTextboxInput = MultimodalValue | None
MultimodalTextboxOutput = MultimodalValue | None

TextboxInput = str | None
TextboxOutput = str | None

AudioInput = str | Tuple[int, np.ndarray] | None
AudioOutput = str | pathlib.Path | bytes | Tuple[int, np.ndarray] | None

# Chat
ChatComponentOutput = DropdownOutput | ChatbotTuplesOutput | MultimodalTextboxOutput
ChatComponentsOutput = ChatComponentOutput | Sequence[ChatComponentOutput] | Iterator[Sequence[ChatComponentOutput]] | None


# Speech
SpeechComponentOutput = TextboxOutput | DropdownOutput | AudioOutput
SpeechComponentsOutput = SpeechComponentOutput | Sequence[SpeechComponentOutput] | None
