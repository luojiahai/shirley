import os
from typing import List
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents.base import Document
from langchain_core.embeddings.embeddings import Embeddings
import langchain_core.vectorstores
from langchain_text_splitters import CharacterTextSplitter

class VectorStore(object):
    def __init__(self) -> None:
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
    def embeddings_model_path(self) -> str:
        return os.path.join(os.getcwd(), 'models', 'all-MiniLM-L6-v2')

    @property
    def vector_store_path(self) -> str:
        return os.path.join(os.getcwd(), 'db', 'chroma_db')

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def client(self) -> langchain_core.vectorstores.VectorStore:
        return self._client

    def index(self, file_path: str) -> None:
        loader = PyPDFLoader(file_path)
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        documents = loader.load_and_split(text_splitter)
        self.client.add_documents(documents)

    def retrieve(self, query: str) -> List[Document]:
        return self.client.similarity_search(query)
