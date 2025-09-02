from google.cloud import storage
import os
from typing import List
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
from app.core.schema.fileSchema import FileMetaData
from datetime import datetime
from google import genai
from google.genai import types
import io

GENAI_API_KEY = os.getenv("GENAI_API_KEY")

class GCSStorageService:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

        if not GENAI_API_KEY:
            raise RuntimeError("GENAI_API_KEY is not set")
        self.genai_client = genai.Client(api_key="AIzaSyAO5d-UQflX90uYqkWxppH6Qrasv3WNEpk")
        # self.genai_client = genai.Client(api_key=GENAI_API_KEY)

    
    def list_files(self, game_id: str = "" ) -> List[str]:
        try:
            full_prefix = f"{game_id}/"
            blobs_iter = self.bucket.list_blobs(prefix=full_prefix)
            return [
                b.name.replace(f"{game_id}/", "", 1)
                for b in blobs_iter
                if not b.name.endswith('/')
            ]
        except Exception as e:
            raise RuntimeError(e)

    def read_file(self, file_path: str) -> str:
        try:
            print("filename from read file", file_path);
            blob = self.bucket.blob(file_path)
            return blob.download_as_text()
        except Exception as e:
            raise RuntimeError(e)
    def upload_file(self, file_path: str, file_content: str, updated_by: str) -> None:
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_content)

            file_name = file_path.rsplit("/", 1)[-1]
            game_name = file_path.split("/", 1)[0]
            print("game_name from upload file", game_name)
            print("file_name from upload file", file_path)
            print("genai_client", self.genai_client)

            if isinstance(file_content, str):
                data = file_content.encode("utf-8")
            else:  # already bytes
                data = file_content

            gemini_file = self.genai_client.files.upload(
            file=io.BytesIO(data),
            config=types.UploadFileConfig(
                mime_type="text/plain",
                display_name=file_name
            ),
        )
            print("gemini_file from upload file", gemini_file)
            print(f"✅ Uploaded to Gemini: {file_name}")

            metaData = FileMetaData(
                fileName=file_name,
                filePath=file_path,
                gameName=game_name,
                createdAt=datetime.utcnow(),
                lastUpdatedAt=datetime.utcnow(),
                raw_preview=file_content[:250],
                geminiUploadTime=datetime.utcnow(),
                geminiFileId=gemini_file.name
            )

            result = fileServices.create_file(
                file=metaData, updatedBy=updated_by, logs_service=logServices
            )
            print("result of create file in firestore", result)
        # except Exception as e:
        #     raise RuntimeError(e)
        except Exception as e:
            import traceback
            print("🔥 Error in upload_file:", e)
            traceback.print_exc()
            raise
    def update_file(self, file_path: str, content: str, updated_by: str) -> None:
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content, content_type="text/plain")
            file_name = file_path.rsplit("/", 1)[-1]
            game_name = file_path.split("/", 1)[0]
            if isinstance(content, str):
                data = content.encode("utf-8")
            else:
                data = content
            gemini_file = self.genai_client.files.upload(
            file=io.BytesIO(data),
            config=types.UploadFileConfig(
                mime_type="text/plain",
                display_name=file_name
            ),
        )
            existing_docs = fileServices.collection.where("filePath", "==", file_path).stream()
            existing_doc = None
            for doc in existing_docs:
                existing_doc = doc
                break
            if not existing_doc:
                raise RuntimeError(f"File metadata not found in Firestore for path: {file_path}")
            file_id = existing_doc.id
            existing_data = existing_doc.to_dict()
            updated_metadata = FileMetaData(
            fileId=file_id,
            fileName=file_name,
            filePath=file_path,
            gameName=game_name,
            createdAt=existing_data.get("createdAt"),
            lastUpdatedAt=datetime.utcnow(),
            geminiUploadTime=datetime.utcnow(),
            geminiFileId=gemini_file.name,
            raw_preview=content[:250]
        )
            result = fileServices.update_file(
            fileId=file_id,
            file=updated_metadata,
            updatedBy=updated_by,
            logs_service=logServices
        )
            print("result of update file in firestore", result)

        except Exception as e:
            raise RuntimeError(e)
    def delete_file(self, file_path: str) -> None:
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            existing_docs = fileServices.collection.where("filePath", "==", file_path).stream()
            existing_doc = next(existing_docs, None)
            if existing_doc:
                fileServices.delete_file(existing_doc.id, logs_service=logServices)
            print(f"✅ Deleted {file_path} and its metadata/logs")
        except Exception as e:
            raise RuntimeError(e)
