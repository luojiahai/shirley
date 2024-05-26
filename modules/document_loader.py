from typing import List
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_core.documents.base import Document
from langchain_text_splitters import CharacterTextSplitter

class DocumentLoader(object):
    def __init__(self) -> None:
        return
    
    def load(self, file_path: str) -> List[Document]:
        # TODO: support other file formats
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        loader = PyPDFLoader(file_path=file_path)
        return loader.load_and_split(text_splitter=text_splitter)
