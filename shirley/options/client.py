from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientOptions:
    local: Optional[bool] = True


@dataclass
class ChatClientOptions(ClientOptions):
    pass


@dataclass
class TextToSpeechClientOptions(ClientOptions):
    pass
