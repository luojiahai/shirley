import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

class Generator(object):
    def __init__(self):
        if not os.path.exists(self.pretrained_model_path):
            raise FileNotFoundError(
                f'Model path {self.pretrained_model_path} not found.'
            )

        if torch.cuda.is_available():
            self._device = torch.device('cuda')
        elif torch.backends.mps.is_available():
            self._device = torch.device('mps')
        else:
            self._device = torch.device('cpu')

        self._model = AutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=self.pretrained_model_path,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
        )

        self._tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=self.pretrained_model_path,
            local_files_only=True,
        )

        self._pipeline = pipeline(
            task='text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
        )

    @property
    def pretrained_model_path(self):
        return os.path.join(os.getcwd(), 'models', 'Mistral-7B-Instruct-v0.2')

    @property
    def device(self):
        return self._device

    @property
    def model(self):
        return self._model

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def pipeline(self):
        return self._pipeline

    def generate(self, prompt: str) -> str:
        text_inputs = [{'role': 'user', 'content': prompt}]
        text_outputs = self.pipeline(
            text_inputs=text_inputs,
            max_new_tokens=256,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        return text_outputs[0]['generated_text']

class VectorStore(object):
    def __init__(self):
        if not os.path.exists(self.embeddings_model_path):
            raise FileNotFoundError(
                f'Model path {self.embeddings_model_path} not found.'
            )

        self._embeddings = HuggingFaceEmbeddings(
            model_name=self.embeddings_model_path
        )

        self._client = Chroma(
            embedding_function=self.embeddings,
            persist_directory=self.vector_store_path
        )

    @property
    def embeddings_model_path(self):
        return os.path.join(os.getcwd(), 'models', 'all-MiniLM-L6-v2')

    @property
    def vector_store_path(self):
        return os.path.join(os.getcwd(), 'db', 'chroma_db')

    @property
    def embeddings(self):
        return self._embeddings

    @property
    def client(self):
        return self._client

    def index(self, file_path: str):
        loader = PyPDFLoader(file_path)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        documents = loader.load_and_split(text_splitter)
        self.client.add_documents(documents)

    def retrieve(self, query: str):
        return self.client.similarity_search(query)

class Augmentor(object):
    def __init__(self):
        system_prompt_path = os.path.join(os.getcwd(), 'system_prompt.txt')
        with open(system_prompt_path, 'r') as file:
            self._system_prompt = file.read()

    @property
    def system_prompt(self):
        return self._system_prompt

    def augment(self, query: str, vector_store: VectorStore):
        max_num_results = 4
        documents = vector_store.retrieve(query)
        search_results = '\n'.join([
            f'{i + 1}. {documents[i].page_content}'
            for i in range(len(documents[:max_num_results]))
        ])
        prompt = self.system_prompt \
            .replace('$search_results$', search_results) \
            .replace('$query$', query)
        return prompt
