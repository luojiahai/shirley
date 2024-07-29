from gradio.components.multimodal_textbox import MultimodalValue
from typing import List, Tuple


Query = RawQuery = str | Tuple[str] | Tuple[str, str] | None
Response = RawResponse = str | Tuple[str] | Tuple[str, str] | None

Chatbot = List[Tuple[Query, Response]]
HistoryState = List[Tuple[RawQuery, RawResponse]]
MultimodalTextbox = MultimodalValue
