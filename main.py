import logging
import shirley
import sys


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

config = shirley.Config()


def load(documents_path: str) -> shirley.Documents:
    document_loader = shirley.DocumentLoader()
    return document_loader.load(directory_path=documents_path)

def index(vector_database: shirley.VectorDatabase, documents: shirley.Documents) -> None:
    vector_database.index(documents)

def retrieve(vector_database: shirley.VectorDatabase, prompt: str) -> str:
    return vector_database.retrieve(prompt)

def augment(prompt: str, documents: shirley.Documents) -> str:
    augmentor = shirley.Augmentor(system_prompt=config.system_prompt)
    return augmentor.augment(prompt, documents)

def main() -> None:
    logger.info('Started')

    prompt = 'Introduce Geoffrey Law. Which university he graduated from? What is his current job?'
    vector_database = shirley.VectorDatabase(persist_directory=config.vector_database_persist_directory)
    documents = load(config.documents_path)
    index(vector_database, documents)
    retrieved_documents = retrieve(vector_database, prompt)
    augmented_prompt = augment(prompt, retrieved_documents)

    # prompt = 'What is potato?'

    generator = shirley.Generator(pretrained_model_path=config.pretrained_model_path)
    generated_text = generator.generate(augmented_prompt)

    logger.info(f'Prompt: {augmented_prompt}')
    logger.info(f'Response: {generated_text}')

    return


if __name__ == '__main__':
    main()
