import torch
import transformers

class Generator(object):
    def __init__(self):
        self._device = 'cpu'
        if torch.cuda.is_available():
            self._device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        self._model = transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path='models/Mistral-7B-Instruct-v0.2',
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )

        self._tokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path='models/Mistral-7B-Instruct-v0.2',
            local_files_only=True,
        )

        self._pipeline = transformers.pipeline(
            task='text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    @property
    def device(self) -> torch.device:
        return self._device
    
    @property
    def model(self) -> transformers.PreTrainedModel:
        return self._model
    
    @property
    def tokenizer(self) -> transformers.PreTrainedTokenizer:
        return self._tokenizer
    
    @property
    def pipeline(self) -> transformers.Pipeline:
        return self._pipeline

    def generate(self, prompt: str) -> str:
        text_inputs: list[dict[str, str]] = [{'role': 'user', 'content': prompt}]
        text_outputs: list[dict[str, str]] = self.pipeline(
            text_inputs=text_inputs,
            return_full_text=False,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=256,
        )
        return text_outputs[0]['generated_text'].strip()
