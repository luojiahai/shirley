import shirley


class Augmentor(object):
    def __init__(self, system_prompt: str) -> None:
        self._system_prompt = system_prompt
        return

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    def augment(self, prompt: str, documents: shirley.Documents) -> str:
        search_results = '\n'.join([
            f'{i + 1}. {documents[i]}'
            for i in range(len(documents))
        ])
        return self.system_prompt \
            .replace('$search_results$', search_results) \
            .replace('$query$', prompt)
