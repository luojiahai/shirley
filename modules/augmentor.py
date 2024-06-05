import os
from modules.vector_database import VectorDatabase

class Augmentor(object):
    def __init__(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def augment(self, query: str, vector_database: VectorDatabase) -> str:
        documents = vector_database.retrieve(query)
        search_results = '\n'.join([
            f'{i + 1}. {documents[i].page_content}'
            for i in range(len(documents))
        ])
        prompt = self.system_prompt \
            .replace('$search_results$', search_results) \
            .replace('$query$', query)
        return prompt
