import os
from typing import List
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents.base import Document
from langchain_core.embeddings.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import CharacterTextSplitter

DEFAULT_EMBEDDINGS_PATH = os.path.join(os.getcwd(), 'models', 'all-MiniLM-L6-v2')
DEFAULT_PERSIST_DIRECTORY = os.path.join(os.getcwd(), 'db', 'chroma_db')

class VectorDatabase(object):
    def __init__(
        self,
        embeddings_path=DEFAULT_EMBEDDINGS_PATH,
        persist_directory=DEFAULT_PERSIST_DIRECTORY
    ) -> None:
        if not os.path.exists(embeddings_path):
            raise FileNotFoundError(
                f'Embeddings path {embeddings_path} not found.'
            )

        self._embeddings = HuggingFaceEmbeddings(
            model_name=embeddings_path
        )

        self._client = Chroma(
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

    @property
    def embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def client(self) -> VectorStore:
        return self._client

    def index(self, file_path: str) -> None:
        loader = PyPDFLoader(file_path)
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        documents = loader.load_and_split(text_splitter)
        self.client.add_documents(documents)

    def retrieve(self, query: str) -> List[Document]:
        return self.client.similarity_search(query)
