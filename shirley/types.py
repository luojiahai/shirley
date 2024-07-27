from typing import List, Tuple


Query = str | Tuple[str] | Tuple[str, str] | None
Response = str | Tuple[str] | Tuple[str, str] | None

Chatbot = List[Tuple[Query, Response]]
TaskHistory = List[Tuple[Query, Response]]
