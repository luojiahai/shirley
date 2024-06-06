import shirley
import os
from modules.config import Config
from modules.utils import flatmap

CONFIG = Config()

def load_and_index(vector_database: shirley.VectorDatabase, clear_database: bool = True) -> None:
    document_loader = shirley.DocumentLoader()
    documents = flatmap(
        lambda file_name: document_loader.load(directory_path=CONFIG.rag_documents_path, file_name=file_name),
        os.listdir(CONFIG.rag_documents_path)
    )
    if clear_database: vector_database.client.delete(vector_database.client.get().get('ids'))
    vector_database.index(documents)

    print('[SHIRLEY] Documents:', list(set([document.metadata['source'] for document in documents])))
    return

def retrieve_and_augment(prompt: str) -> str:
    vector_database = shirley.VectorDatabase(
        embeddings_path=CONFIG.embeddings_path,
        persist_directory=CONFIG.database_persist_directory
    )
    if CONFIG.rag_index_enabled: load_and_index(vector_database)
    documents = vector_database.retrieve(prompt)

    augmentor = shirley.Augmentor(
        system_prompt=CONFIG.system_prompt
    )
    return augmentor.augment(prompt, documents)

def main() -> None:
    print('[SHIRLEY] Hello, World!')

    prompt = CONFIG.prompt

    if CONFIG.rag_enabled: prompt = retrieve_and_augment(prompt)

    generator = shirley.Generator(
        pretrained_model_path=CONFIG.pretrained_model_path
    )
    generated_text = generator.generate(prompt)

    print('[SHIRLEY] Prompt:', prompt)
    print('[SHIRLEY] Response:', generated_text[-1]['content'])
    return

if __name__ == '__main__':
    main()
