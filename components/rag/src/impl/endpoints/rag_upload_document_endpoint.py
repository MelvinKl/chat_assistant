import asyncio
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory

from base_component_api.endpoints.upload_document_endpoint import UploadDocumentEndpoint
from base_library.document_extractor.extractor import Extractor
from base_library.vector_database.vector_database import VectorDatabase
from fastapi import File, UploadFile
from langchain_unstructured import UnstructuredLoader
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared


class RagUploadDocument(UploadDocumentEndpoint):

    @inject.autoparams()
    def __init__(
        self,
        pdf_extractor: Extractor,
        vector_database: VectorDatabase,
    ):
        self._pdf_extractor = pdf_extractor
        self._vector_database = vector_database
        self._unstructured_client = UnstructuredClient(server_url="http://unstructured:8000")

    def upload_documents(self, file: UploadFile = File(...)) -> None:
        try:
            with TemporaryDirectory() as tmpdirname:
                # Copy content from UploadFile to SpooledTemporaryFile
                temp_file_name = Path(tmpdirname) / file.filename
                with temp_file_name.open("wb") as tmpfile:
                    copyfileobj(file.file, tmpfile)
                unstructured = UnstructuredLoader(
                    client=self._unstructured_client,
                    chunking_strategy=shared.ChunkingStrategy.BY_TITLE,
                    file_path=temp_file_name,
                    partition_via_api=True,
                    strategy=shared.Strategy.OCR_ONLY,
                    languages=["deu", "eng"],
                    pdf_infer_table_structure=True,
                )
                extracted_content = unstructured.load()
                self._vector_database.upload_documents(extracted_content)
        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

        return {"message": f"Successfully uploaded {file.filename}"}
