from gradio.components import Component
from gradio.components.multimodal_textbox import MultimodalValue
from models.qwen_vl_chat.qwen_generation_utils import HistoryType
from typing import Iterator, List, Sequence, Tuple


ChatHistory = HistoryType

Query = RawQuery = str | Tuple[str] | Tuple[str, str] | None
Response = RawResponse = str | Tuple[str] | Tuple[str, str] | None

ChatbotTuplesInput = ChatbotTuplesOutput = List[Tuple[Query, Response]]
HistoryInput = HistoryOutput = List[Tuple[RawQuery, RawResponse]]
MultimodalTextboxInput = MultimodalTextboxOutput = MultimodalValue

BlockInput = ChatbotTuplesInput | HistoryInput | MultimodalTextboxInput
BlockOutput = ChatbotTuplesOutput | HistoryOutput | MultimodalTextboxOutput

BlocksOutput = BlockOutput | Sequence[BlockOutput] | Iterator[Sequence[BlockOutput]] | None
ComponentsOutput = Component | Sequence[Component] | None
