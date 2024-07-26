import pypdf
from typing import List


Document = str
Documents = List[Document]


class DocumentLoader(object):

    def __init__(self) -> None:
        return

    def load_file(self, file_path: str) -> Document:
        if file_path.endswith('.pdf'):
            return self._load_pdf(file_path=file_path)
        # TODO: support other file formats
        return ''

    def _load_pdf(self, file_path: str) -> Document:
        reader = pypdf.PdfReader(stream=file_path)
        return '\n'.join([page.extract_text() for page in reader.pages])
