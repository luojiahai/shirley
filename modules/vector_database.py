import os
from typing import List
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents.base import Document
from langchain_core.embeddings.embeddings import Embeddings

class VectorDatabase(object):
    def __init__(self, embeddings_path: str, persist_directory: str) -> None:
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
    def client(self) -> Chroma:
        return self._client

    def index(self, documents: List[Document]) -> None:
        self.client.add_documents(documents=documents)

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        return self.client.similarity_search(query=query, k=k)
