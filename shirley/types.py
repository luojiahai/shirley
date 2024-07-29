from gradio.components.multimodal_textbox import MultimodalValue
from typing import List, Tuple


Query = RawQuery = str | Tuple[str] | Tuple[str, str] | None
Response = str | Tuple[str] | Tuple[str, str] | None

Chatbot = List[Tuple[Query, Response] | List[Query, Response]]
HistoryState = List[Tuple[RawQuery, Response]]
MultimodalTextbox = MultimodalValue
