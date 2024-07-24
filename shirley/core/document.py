import os
import shirley.utils
import pypdf
from typing import List


Document = str
Documents = List[Document]


class DocumentLoader(object):
    def __init__(self) -> None:
        return

    def load(self, directory_path: str) -> Documents:
        return shirley.utils.flatmap(
            lambda file_name: self._load_file(os.path.join(os.getcwd(), directory_path, file_name)),
            os.listdir(directory_path)
        )

    def _load_file(self, file_path: str) -> Documents:
        if file_path.endswith('.pdf'):
            return self._load_pdf(file_path=file_path)
        # TODO: support other file formats
        return []

    def _load_pdf(self, file_path: str) -> Documents:
        # TODO: split text
        reader = pypdf.PdfReader(stream=file_path)
        return [page.extract_text() for page in reader.pages]
