from pathlib import Path
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile, TemporaryDirectory

from base_library.document_extractor.extractor import Extractor
from base_library.vector_database.vector_database import VectorDatabase
from fastapi import File, UploadFile

from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint


class RagUploadDocument(UploadDocumentEndpoint):

    def __init__(
        self,
        pdf_extractor: Extractor,
        vector_database: VectorDatabase,
    ):
        self._pdf_extractor = pdf_extractor
        self._vector_database = vector_database

    def upload_documents(self, file: UploadFile = File(...)) -> None:
        try:
            with TemporaryDirectory() as tmpdirname:
                # Copy content from UploadFile to SpooledTemporaryFile
                temp_file_name = Path(tmpdirname) / "tmp.pdf"
                with temp_file_name.open("wb") as tmpfile:
                    copyfileobj(file.file, tmpfile)

                extracted_content = self._pdf_extractor.extract(temp_file_name)
                self._vector_database.upload_documents(extracted_content)
        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        return {"message": f"Successfully uploaded {file.filename}"}
