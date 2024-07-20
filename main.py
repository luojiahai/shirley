import os
import shirley
from langchain_core.documents.base import Document
from shirley.utils import flatmap
from typing import List

CONFIG = shirley.Config()

def load(documents_path: str) -> List[Document]:
    document_loader = shirley.DocumentLoader()
    documents = flatmap(
        lambda file_name: document_loader.load(directory_path=documents_path, file_name=file_name),
        os.listdir(documents_path)
    )
    return documents

def index(vector_database: shirley.VectorDatabase, documents: List[Document]) -> None:
    vector_database.index(documents)

def retrieve(vector_database: shirley.VectorDatabase, prompt: str) -> str:
    return vector_database.retrieve(prompt)

def augment(prompt: str, documents: List[Document]) -> str:
    augmentor = shirley.Augmentor(system_prompt=CONFIG.system_prompt)
    return augmentor.augment(prompt, documents)

def main() -> None:
    # prompt = 'Introduce Geoffrey Law. Which university he graduated from? What is his current job?'
    # vector_database = shirley.VectorDatabase(
    #     embeddings_path=CONFIG.embeddings_path,
    #     persist_directory=CONFIG.database_persist_directory
    # )
    # documents = load(CONFIG.documents_path)
    # index(vector_database, documents)
    # retrieved_documents = retrieve(vector_database, prompt)
    # augmented_prompt = augment(prompt, retrieved_documents)

    prompt = 'What is potato?'

    generator = shirley.Generator(pretrained_model_path=CONFIG.pretrained_model_path)
    generated_text = generator.generate(prompt)

    print('[shirley] prompt:', prompt)
    print('[shirley] response:', generated_text)
    return

if __name__ == '__main__':
    main()
