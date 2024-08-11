from dataclasses import dataclass


@dataclass
class ClientOptions:
    local: bool


@dataclass
class ChatClientOptions(ClientOptions):
    pass


@dataclass
class TextToSpeechClientOptions(ClientOptions):
    pass
