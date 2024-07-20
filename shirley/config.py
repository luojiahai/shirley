import configparser
from shirley.utils import getpath, read

class Config(object):
    def __init__(self) -> None:
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')
        return

    @property
    def documents_path(self) -> str:
        return getpath(self._config['DEFAULT']['DOCUMENTS_PATH'])

    @property
    def embeddings_path(self) -> str:
        return getpath(self._config['DEFAULT']['EMBEDDINGS_PATH'])

    @property
    def pretrained_model_path(self) -> str:
        return getpath(self._config['DEFAULT']['PRETRAINED_MODEL_PATH'])

    @property
    def database_persist_directory(self) -> str:
        return getpath(self._config['DEFAULT']['DATABASE_PERSIST_DIRECTORY'])

    @property
    def system_prompt(self) -> str:
        return read(getpath(self._config['DEFAULT']['SYSTEM_PROMPT_PATH']))
