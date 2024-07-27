from typing import List, Tuple


Query = RawQuery = str | Tuple[str] | Tuple[str, str] | None
Response = str | Tuple[str] | Tuple[str, str] | None

Chatbot = List[Tuple[Query, Response]] # [(<query>, <response>)]
HistoryState = List[Tuple[RawQuery, Response]] # [(<raw_query>, <response>)]
FileExplorer = str | List[str]
