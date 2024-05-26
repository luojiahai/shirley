import os
import itertools
from typing import Any, Callable, List, TypeVar
import shirley

T = TypeVar('T')

def flatmap(callback: Callable[[Any], List[T]], iterable: List[Any]) -> List[T]:
    return list(itertools.chain.from_iterable(map(callback, iterable)))

def main():
    print('[SHIRLEY] Hello, World!')

    file_names = [
        'resume.pdf'
    ]

    document_loader = shirley.DocumentLoader()
    documents = flatmap(
        lambda file_name: document_loader.load(file_path=os.path.join(os.getcwd(), 'resources', file_name)),
        file_names
    )

    vector_database = shirley.VectorDatabase()
    vector_database.index(documents)
    print('[SHIRLEY] Documents:', list(set([document.metadata['source'] for document in documents])))

    augmentor = shirley.Augmentor()
    query = 'Introduce Geoffrey Law. Which university he graduated from? What is his current job?'
    prompt = augmentor.augment(query, vector_database)

    # prompt = 'What is potato?'

    print('[SHIRLEY] Prompt:', prompt)

    generator = shirley.Generator()
    generated_text = generator.generate(prompt)
    print('[SHIRLEY] Response:', generated_text[-1]['content'])

if __name__ == '__main__':
    main()
