import os
from typing import List
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import CharacterTextSplitter

class DocumentLoader(object):
    def __init__(self) -> None:
        return
    
    def load(self, directory_path: str, file_name: str) -> List[Document]:
        file_path = os.path.join(os.getcwd(), directory_path, file_name)
        # TODO: support other file formats
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        loader = PyPDFLoader(file_path=file_path)
        return loader.load_and_split(text_splitter=text_splitter)
