import logging
import os
import pathlib
import shirley as sh
import sys
import torch
import transformers
import uuid
from .client import Client
from collections import OrderedDict
from shirley.options import ChatClientOptions
from typing import Any, Dict, Generator, List


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class Chat(Client):

    def __init__(self, options: ChatClientOptions = ChatClientOptions()) -> None:
        super().__init__(options=options)

        self._local = options.local
        self._pretrained_model_name_or_path: str | None = None
        self._device: torch.device | None = torch.device('cpu')
        self._device_name: str | None = None
        self._tokenizer: transformers.PreTrainedTokenizer | None = None
        self._model: transformers.PreTrainedModel | None = None


    @property
    def pretrained_model_name_or_path(self) -> str | None:
        return self._pretrained_model_name_or_path

    @property
    def model(self) -> transformers.PreTrainedModel | None:
        return self._model


    def get_models(self) -> List[str]:
        if self._local:
            models_directory = os.path.abspath(os.path.expanduser('./models'))
            pretrained_models = [
                filename for filename in os.listdir(models_directory)
                if os.path.isdir(os.path.join(models_directory, filename))
            ]
            return pretrained_models
        else:
            return ['Qwen/Qwen-VL-Chat']


    def get_model_name_or_path(self, model_name: str) -> str:
        if self._local:
            return os.path.abspath(os.path.expanduser(f'./models/{model_name}'))
        else:
            return model_name


    def get_model_config(self) -> Dict | None:
        if not self._model:
            return None

        model_config = self._model.config.to_dict()
        return OrderedDict([
            ('device', self._device),
            ('device_name', self._device_name),
            ('architectures', model_config['architectures']),
            ('bf16', model_config['bf16']),
            ('fp16', model_config['fp16']),
            ('fp32', model_config['fp32']),
            ('model_type', model_config['model_type']),
            ('tokenizer_type', model_config['tokenizer_type']),
            ('torch_dtype', model_config['torch_dtype']),
            ('transformers_version', model_config['transformers_version']),
        ])


    def load_model(self, pretrained_model_name_or_path: str) -> None:
        if not os.path.exists(pretrained_model_name_or_path):
            logger.warning(f'Pre-trained model not found in path \'{pretrained_model_name_or_path}\'.')
            logger.info(f'Using remote pre-trained model \'{pretrained_model_name_or_path}\' from 🤗 Hugging Face.')
            local_files_only = False
        else:
            logger.info(f'Using local pre-trained model \'{pretrained_model_name_or_path}\'.')
            local_files_only = True

        self._pretrained_model_name_or_path = pretrained_model_name_or_path

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
            self._device_name = torch.cuda.get_device_name(torch.cuda.current_device())
        # elif torch.backends.mps.is_available():
        #     self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        tokenizer: transformers.PreTrainedTokenizer = transformers.AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            local_files_only=local_files_only,
            trust_remote_code=True,
        )

        model: transformers.PreTrainedModel = transformers.AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            local_files_only=local_files_only,
            trust_remote_code=True,
        )

        model.generation_config = transformers.GenerationConfig.from_pretrained(
            pretrained_model_name=pretrained_model_name_or_path,
            local_files_only=local_files_only,
            trust_remote_code=True,
        )

        if model.generation_config.pad_token_id is not None:
            model.generation_config.pad_token_id = torch.tensor(
                data=[model.generation_config.pad_token_id],
                device=self._device,
            )
        if model.generation_config.eos_token_id is not None:
            model.generation_config.eos_token_id = torch.tensor(
                data=[model.generation_config.eos_token_id],
                device=self._device,
            )

        self._tokenizer = tokenizer
        self._model = model.to(device=self._device)


    def chat_stream(self, query: sh.types.QwenQuery, history: sh.types.QwenHistory = None) -> Generator[str, Any, None]:
        return self._model.chat_stream(tokenizer=self._tokenizer, query=query, history=history)


    def draw_bbox_on_latest_picture(self, history: sh.types.QwenHistory) -> str | None:
        response = history[-1][1]
        image = self._tokenizer.draw_bbox_on_latest_picture(response=response, history=history)
        if image is not None:
            images_tempdir = pathlib.Path(self.tempdir) / 'images'
            images_tempdir.mkdir(exist_ok=True, parents=True)
            name = f'img-{uuid.uuid4()}.jpg'
            filename = images_tempdir / name
            image.save(str(filename))
            logger.info(f'Image file saved in {str(filename)}.')
            return str(filename)
        return None
