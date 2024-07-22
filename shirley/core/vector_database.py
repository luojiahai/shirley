import chromadb
import chromadb.config
import shirley
import uuid


class VectorDatabase(object):
    def __init__(self, persist_directory: str, reset: bool = True) -> None:
        client_settings = chromadb.config.Settings(
            is_persistent=True,
            persist_directory=persist_directory,
            allow_reset=reset
        )
        self._client = chromadb.Client(settings=client_settings)
        if reset: self._client.reset()
        self._collection = self._client.get_or_create_collection(name='default')
        return

    @property
    def client(self) -> chromadb.ClientAPI:
        return self._client
    
    @property
    def collection(self) -> chromadb.Collection:
        return self._collection

    def index(self, documents: shirley.Documents) -> None:
        ids = [str(uuid.uuid4()) for _ in documents]
        self.collection.upsert(ids=ids, documents=documents)

    def retrieve(self, query: str, k: int = 4) -> shirley.Documents:
        return self.collection.query(query_texts=[query], n_results=k)['documents'][0]
