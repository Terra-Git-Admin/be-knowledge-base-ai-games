import os
from google.cloud import storage
from fastapi import HTTPException, status
from typing import List
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
from app.core.schema.fileSchema import FileMetaData, EtherPadState
from datetime import datetime
from google import genai
from google.genai import types
import io
import requests
import json
from dotenv import load_dotenv
from app.core.generalFunctions import generalFunction
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

            gemini_file_id = generalFunction.gemini_upload(file_name=file_name, file_content=file_content)

            # 3. Create metadata and save to Firestore (no change here)
            metaData = FileMetaData(
                fileName=file_name,
                filePath=file_path,
                gameName=game_name,
                createdAt=datetime.utcnow(),
                lastUpdatedAt=datetime.utcnow(),
                raw_preview=file_content[:250],
                geminiUploadTime=datetime.utcnow(),
                geminiFileId=gemini_file_id,
                isDeleted=False,
                etherpad=EtherPadState()
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
    def update_file(self, file_path: str, content: str, updated_by: str, lastSavedRevision: int) -> None:
        try:
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(content, content_type="text/plain")
            file_name = file_path.rsplit("/", 1)[-1]
            game_name = file_path.split("/", 1)[0]
            gemini_file_id = generalFunction.gemini_upload(file_name=file_name, file_content=content)

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
            geminiFileId=gemini_file_id,
            raw_preview=content[:250],
            isDeleted= False,
            etherpad=EtherPadState(
                lastSavedRevision=lastSavedRevision,
                lastSavedAt=datetime.utcnow(),
                unsaved=False
            )
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
    def rename_file(self, old_path: str, new_path: str, username: str) -> None:
        try:
            if not old_path or not new_path:
                raise HTTPException(status_code=400, detail="old_path and new_path are required")
            if old_path == new_path:
                raise HTTPException(status_code=400, detail="old_path and new_path are identical")

            # 1) Ensure Firestore has a doc for the old_path
            old_docs = list(fileServices.collection.where("filePath", "==", old_path).limit(1).stream())
            if not old_docs:
                raise HTTPException(status_code=404, detail=f"Metadata not found in Firestore for {old_path}")

            old_doc = old_docs[0]
            file_id = old_doc.id
            existing_data = old_doc.to_dict() or {}

            # 2) Prevent conflicts in Firestore and Bucket
            existing_new = list(fileServices.collection.where("filePath", "==", new_path).limit(1).stream())
            if existing_new:
                raise HTTPException(status_code=400, detail=f"File with path {new_path} already exists in Firestore")

            dest_blob = self.bucket.blob(new_path)
            if dest_blob.exists():
                raise HTTPException(status_code=400, detail=f"Destination object {new_path} already exists in bucket")

            src_blob = self.bucket.blob(old_path)
            if not src_blob.exists():
                raise HTTPException(status_code=404, detail=f"Source object not found: {old_path}")

            # 3) Copy file in bucket
            try:
                self.bucket.copy_blob(src_blob, self.bucket, new_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to copy object: {str(e)}")

            # 4) Update Firestore metadata
            try:
                existing_etherpad = existing_data.get("etherpad", {})
                updated_metadata = FileMetaData(
                    fileId=file_id,
                    fileName=new_path.rsplit("/", 1)[-1],
                    filePath=new_path,
                    gameName=new_path.split("/", 1)[0],
                    createdAt=existing_data.get("createdAt", datetime.utcnow()),
                    lastUpdatedAt=datetime.utcnow(),
                    raw_preview=existing_data.get("raw_preview", "") or "",
                    geminiUploadTime=existing_data.get("geminiUploadTime"),
                    geminiFileId=existing_data.get("geminiFileId"),
                    isDeleted=existing_data.get("isDeleted", False),
                    etherpad=EtherPadState(
                        lastSavedRevision=existing_etherpad.get("lastSavedRevision", 0),lastSavedAt=existing_etherpad.get("lastSavedAt"),
                        unsaved=existing_etherpad.get("unsaved", False),
                    )
                )
                fileServices.update_file(
                    fileId=file_id,
                    file=updated_metadata,
                    updatedBy=username,
                    logs_service=logServices
                )
            except Exception as e:
                # rollback the bucket copy since Firestore update failed
                try:
                    dest_blob.delete()
                except Exception as cleanup_err:
                    print(f"⚠️ Rollback failed: {cleanup_err}")
                raise HTTPException(status_code=500, detail=f"Failed to update Firestore metadata: {str(e)}")

            # 5) If Firestore update succeeds → delete old blob
            try:
                src_blob.delete()
            except Exception as e:
                # non-fatal, but log it
                print(f"⚠️ Warning: Failed to delete old blob {old_path}: {e}")

        except Exception as e:
            raise RuntimeError(e)

    def search_file_content(self, search_query: str, game_id: str) -> List[str]:
        files = self.list_files(game_id)
        matching_files = []
        print("🔍 Searching for:", search_query)
        print("🔍 Files to search:", files)
        for file in files:
            try:
                content = self.read_file(f"{game_id}/{file}")
                if search_query.lower() in content.lower():
                    print(f"✅ Found match in {file}")
                    print(f"✅ Content: {content}")
                    matching_files.append(f"{game_id}/{file}")
            except Exception as e:
                print(f"Failed to search file content: {e}")
        return matching_files

googleStorageService = GCSStorageService(db)
