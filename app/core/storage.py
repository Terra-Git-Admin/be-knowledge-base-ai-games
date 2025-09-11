import os
from google.cloud import storage
from fastapi import HTTPException, status
from typing import List
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
from app.core.schema.fileSchema import FileMetaData
from datetime import datetime
from google import genai
from google.genai import types
import io
import requests
import json
from dotenv import load_dotenv
load_dotenv()

GENAI_API_KEY = os.getenv("GENAI_API_KEY")
db = os.getenv("DATABASE")

class GCSStorageService:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.gemini_api_key = os.getenv("GENAI_API_KEY")
        if not self.gemini_api_key:
            raise RuntimeError("GENAI_API_KEY is not set")
        self.genai_client = genai.Client(api_key=self.gemini_api_key)

    def list_games(self) -> List[str]:
        try:
            blobs = self.bucket.list_blobs()
            games = set()
            for blob in blobs:
                parts = blob.name.split("/", 1)  # take text before first "/"
                if parts and parts[0]:
                    games.add(parts[0])

            games_list = sorted(list(games))
            print("games from bucket", games_list)
            return games_list
        except Exception as e:
            raise RuntimeError(f"Failed to list games: {e}")
    
    def debug_list(self):
        blobs = list(self.bucket.list_blobs())
        for b in blobs:
            print("BLOB:", b.name)
    
    def create_game(self, game_id: str) -> str:
        try:
            placeholder_blob = self.bucket.blob(f"{game_id}/.keep")
            placeholder_blob.upload_from_string("")
            return f"Game folder {game_id} created."
        except Exception as e:
            raise RuntimeError(f"Failed to create game: {e}")
    
    def delete_game(self, game_id: str) -> str:
        try:
            blobs = self.bucket.list_blobs(prefix=f"{game_id}/")
            for blob in blobs:
                blob.delete()
            return f"Game folder {game_id} deleted."
        except Exception as e:
            raise RuntimeError(f"Failed to delete game: {e}")

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
        """
        Uploads a file to Google Cloud Storage and the Gemini File API via a direct REST call.
        """
        existing = list(fileServices.collection.where("filePath", "==", file_path).limit(1).stream())
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"File with path {file_path} already exists"
            )
        try:
        # 1. Upload to your Google Cloud Storage (no change here)
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_content)

            file_name = file_path.rsplit("/", 1)[-1]
            game_name = file_path.split("/", 1)[0]

            # 2. Prepare and execute the direct API call to Gemini (SDK replacement)
            gemini_upload_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={self.gemini_api_key}"
        
            metadata_payload = {"file": {"display_name": file_name}}
        
            # Structure for multipart/form-data request
            files_payload = {
                'metadata': (None, json.dumps(metadata_payload), 'application/json'),
                'file': (file_name, file_content, 'text/plain'), # (filename, file_data, content_type)
            }

            print(f"✅ Calling Gemini REST API to upload '{file_name}'...")
            response = requests.post(gemini_upload_url, files=files_payload)
        
            # This will raise an error for 4xx/5xx responses, which is caught by the except block
            response.raise_for_status() 
        
            response_data = response.json()
            gemini_file_id = response_data['file']['name']

            print(f"✅ Successfully uploaded to Gemini. File ID: {gemini_file_id}")

            # 3. Create metadata and save to Firestore (no change here)
            metaData = FileMetaData(
                fileName=file_name,
                filePath=file_path,
                gameName=game_name,
                createdAt=datetime.utcnow(),
                lastUpdatedAt=datetime.utcnow(),
                raw_preview=file_content[:250],
                geminiUploadTime=datetime.utcnow(),
                geminiFileId=gemini_file_id, # Use the ID from the API response
                isDeleted=False
            )

            result = fileServices.create_file(
                file=metaData, updatedBy=updated_by, logs_service=logServices
            )
            print("result of create file in firestore", result)
    
        except requests.exceptions.HTTPError as http_err:
            # Specific handling for failed API calls to get more details
            print(f"🔥 Gemini API upload failed with status code: {http_err.response.status_code}")
            print(f"🔥 Response Body: {http_err.response.text}")
            raise HTTPException(status_code=500, detail=f"Failed to upload to Gemini: {http_err.response.text}")
    
        except Exception as e:
            import traceback
            print("🔥 An unexpected error occurred in upload_file:", e)
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
            raw_preview=content[:250],
            isDeleted= False
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

googleStorageService = GCSStorageService("db")
