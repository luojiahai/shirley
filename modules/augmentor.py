from typing import List
from langchain_core.documents.base import Document

class Augmentor(object):
    def __init__(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt
        return

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def augment(self, prompt: str, documents: List[Document]) -> str:
        search_results = '\n'.join([
            f'{i + 1}. {documents[i].page_content}'
            for i in range(len(documents))
        ])
        return self.system_prompt \
            .replace('$search_results$', search_results) \
            .replace('$query$', prompt)
