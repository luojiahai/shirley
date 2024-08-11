from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ChatbotOptions:
    avatar_images: Optional[Tuple] = None
