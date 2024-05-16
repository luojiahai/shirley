from typing import Dict, List, TypeAlias, Union # type: ignore
import torch
import transformers
from transformers.generation.utils import GenerateOutput
from transformers.models.auto.modeling_auto import AutoModelForCausalLM
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.modeling_utils import PreTrainedModel
from transformers.tokenization_utils import PreTrainedTokenizer
from transformers.tokenization_utils_base import BatchEncoding
from transformers.tokenization_utils_fast import PreTrainedTokenizerFast
from utils import initialization, generation

Model: TypeAlias = PreTrainedModel
Tokenizer: TypeAlias = Union[PreTrainedTokenizer, PreTrainedTokenizerFast]
Conversation: TypeAlias = List[Dict[str, str]]
TokenizedChat: TypeAlias = Union[str, List[int], List[str], List[List[int]], BatchEncoding]
Output: TypeAlias = Union[GenerateOutput, torch.LongTensor]

class App(object):
    """
    Attributes
    ----------
    device : torch.device
        Torch device

    Methods
    -------
    generate(prompt)
        Generates output using the model given the prompt
    """

    @initialization
    def __init__(self, model_path: str):
        print('Torch version:', torch.__version__)
        print('Transformers version:', transformers.__version__)

        self.device = self._get_device()
        print('Torch device:', self.device)

        self.model = self._get_model(model_path)
        print('Model:', self.model.name_or_path)

        self.tokenizer = self._get_tokenizer(model_path)
        print('Tokenizer:', self.tokenizer.name_or_path)

    def _get_device(self) -> torch.device:
        device = torch.device('cpu')
        use_cuda = torch.cuda.is_available()
        use_mps = torch.backends.mps.is_available()
        if use_cuda:
            device = torch.device('cuda')
            print('CUDA:', torch.cuda.get_device_properties('cuda').name)
        elif use_mps:
            # https://developer.apple.com/metal/pytorch/
            device = torch.device('mps')
        else:
            device = torch.device('cpu')
        return device

    def _get_model(self, model_path: str) -> Model:
        model: Model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=model_path,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )
        return model.to(device=self.device)

    def _get_tokenizer(self, model_path: str) -> Tokenizer:
        tokenizer: Tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=model_path,
            local_files_only=True,
        )
        return tokenizer

    def _get_conversation(self, prompt: str) -> Conversation:
        conversation: Conversation = [
            {'role': 'user', 'content': prompt},
        ]
        return conversation

    def _get_tokenized_chat(self, tokenizer: Tokenizer, conversation: Conversation) -> TokenizedChat:
        tokenized_chat: TokenizedChat = tokenizer.apply_chat_template(
            conversation=conversation,
            return_tensors='pt'
        )
        return tokenized_chat.to(device=self.device)

    def _get_output(self, model: Model, tokenizer: Tokenizer, tokenized_chat: TokenizedChat) -> Output:
        output: Output = model.generate(
            inputs=tokenized_chat,
            max_length=256,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
        return output

    @generation
    def generate(self, prompt: str) -> List[str]:
        conversation = self._get_conversation(prompt)
        tokenized_chat = self._get_tokenized_chat(self.tokenizer, conversation)
        output = self._get_output(self.model, self.tokenizer, tokenized_chat)
        return self.tokenizer.batch_decode(output)
