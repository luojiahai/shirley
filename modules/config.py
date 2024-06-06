import configparser
from modules.utils import getpath, read

class Config(object):
    def __init__(self) -> None:
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')
        return
    
    @property
    def rag_enabled(self) -> bool:
        return self._config['DEFAULT'].getboolean('RAG_ENABLED')

    @property
    def rag_index_enabled(self) -> bool:
        return self._config['DEFAULT'].getboolean('RAG_INDEX_ENABLED')
    
    @property
    def rag_documents_path(self) -> str:
        return getpath(self._config['DEFAULT']['RAG_DOCUMENTS_PATH'])
    
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
        
    @property
    def prompt(self) -> str:
        return read(getpath(self._config['DEFAULT']['PROMPT_PATH']))
