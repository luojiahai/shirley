import configparser
import shirley.utils


class Config(object):
    def __init__(self) -> None:
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')
        return

    @property
    def documents_path(self) -> str:
        return shirley.utils.getpath(self._config['DEFAULT']['DOCUMENTS_PATH'])

    @property
    def pretrained_model_path(self) -> str:
        return shirley.utils.getpath(self._config['DEFAULT']['PRETRAINED_MODEL_PATH'])

    @property
    def vector_database_persist_directory(self) -> str:
        return shirley.utils.getpath(self._config['DEFAULT']['VECTOR_DATABASE_PERSIST_DIRECTORY'])

    @property
    def system_prompt(self) -> str:
        return shirley.utils.read(shirley.utils.getpath(self._config['DEFAULT']['SYSTEM_PROMPT_PATH']))
