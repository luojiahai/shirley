import sys, os
from generator import Generator
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_text_splitters import CharacterTextSplitter

def main():
    print('Hello, World!')
    print()

    prompt = 'What is potato?'

    print('BEGIN PRINT PROMPT')
    print(prompt)
    print('END PRINT PROMPT')
    print()

    print('BEGIN INITIALIZATION')
    generator = Generator()
    print('Device:', generator.device)
    print('END INITIALIZATION')
    print()

    print('BEGIN GENERATION')
    generated_text = generator.generate(prompt)
    print('END GENERATION')
    print()

    print('BEGIN PRINT GENERATED TEXT')
    print(generated_text)
    print('END PRINT GENERATED TEXT')
    print()

def test():
    loader = PyPDFLoader("resources/resume.pdf")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    db = Chroma(embedding_function=embedding_function, persist_directory="db/chroma_db")

    db.add_documents(docs)

    query = "What is Geoffrey's current job?"
    docs = db.similarity_search(query)

    print(docs[0].page_content)

if __name__ == '__main__':
    path = os.path.realpath('.')
    if path not in sys.path:
        sys.path.append(path)

    main()
    # test()
