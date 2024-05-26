import os
from modules.vector_database import VectorDatabase

class Augmentor(object):
    def __init__(self) -> None:
        system_prompt_path = os.path.join(os.getcwd(), 'system_prompt.txt')
        with open(system_prompt_path, 'r') as file:
            self._system_prompt = file.read()

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def augment(self, query: str, vector_database: VectorDatabase) -> str:
        max_num_results = 4
        documents = vector_database.retrieve(query)
        search_results = '\n'.join([
            f'{i + 1}. {documents[i].page_content}'
            for i in range(len(documents[:max_num_results]))
        ])
        prompt = self.system_prompt \
            .replace('$search_results$', search_results) \
            .replace('$query$', query)
        return prompt
