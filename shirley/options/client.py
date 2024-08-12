from dataclasses import dataclass
from typing import Optional


@dataclass
class ClientOptions:
    pass


@dataclass
class ChatClientOptions(ClientOptions):
    local: Optional[bool] = True


@dataclass
class TextToSpeechClientOptions(ClientOptions):
    pass
