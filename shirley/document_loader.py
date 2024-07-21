import os
import shirley
import shirley.utils
import pypdf


class DocumentLoader(object):
    def __init__(self) -> None:
        return

    def load(self, directory_path: str) -> shirley.Documents:
        return shirley.utils.flatmap(
            lambda file_name: self._load_file(os.path.join(os.getcwd(), directory_path, file_name)),
            os.listdir(directory_path)
        )

    def _load_file(self, file_path: str) -> shirley.Documents:
        if file_path.endswith('.pdf'):
            return self._load_pdf(file_path=file_path)
        # TODO: support other file formats
        return []

    def _load_pdf(self, file_path: str) -> shirley.Documents:
        # TODO: split text
        reader = pypdf.PdfReader(stream=file_path)
        return [page.extract_text() for page in reader.pages]
