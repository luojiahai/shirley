from .client import ClientOptions
from .components import ChatbotOptions
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class InterfaceOptions:
    pass


@dataclass
class HeaderInterfaceOptions(InterfaceOptions):
    title: Optional[str] = '🦈 Shirley WebUI'
    description: Optional[str] = 'It is just doing some stuff intelligently. \
        This WebUI is built by [luojiahai](https://luojiahai.com).'


@dataclass
class FooterInterfaceOptions(InterfaceOptions):
    pass


@dataclass
class ChatInterfaceOptions(InterfaceOptions):
    client: Optional[ClientOptions] = ClientOptions(local=True)
    chatbot: Optional[ChatbotOptions] = ChatbotOptions()
    chat_stream_fn: Optional[Callable] = None


@dataclass
class TextToSpeechInterfaceOptions(InterfaceOptions):
    client: Optional[ClientOptions] = ClientOptions(local=False)
