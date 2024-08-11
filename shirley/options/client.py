from dataclasses import dataclass


@dataclass
class ClientOptions:
    pass


@dataclass
class ChatClientOptions(ClientOptions):
    local: bool


@dataclass
class TextToSpeechClientOptions(ClientOptions):
    pass
