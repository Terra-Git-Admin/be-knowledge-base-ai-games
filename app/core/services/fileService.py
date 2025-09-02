from fastapi import FastAPI
from google.cloud import firestore
from app.core.schema.fileSchema import FileMetaData
from app.core.services.logService import LogServices
from app.core.schema.logsSchema import Logs
from typing import Dict, List, Optional
from datetime import datetime
from app.core.services.logService import LogServices

db = firestore.Client(project="aigameschat", database="school-game")


class FileServices:
    COLLECTION_NAME = "files"

    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)

    def create_file(
        self, file: FileMetaData, updatedBy: str, logs_service: LogServices
    ) -> Dict:
        doc_ref = self.collection.document(file.fileId)
        if doc_ref.get().exists:
            return {"error": "File already exists"}
        doc_ref.set(file.dict(exclude_none=True))
        log = Logs(fileId=file.fileId, updatedBy=updatedBy)
        logs_service.create_log(log)
        return {"message": "File created successfully"}

    def list_files(self, gameName: str) -> List[FileMetaData]:
        query = self.collection.where("gameName", "==", gameName)
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def list_file(self, fileId: str) -> FileMetaData:
        doc_ref = self.collection.document(fileId)
        if not doc_ref.get().exists:
            return {"error": "File not found"}
        doc = doc_ref.get()
        return doc.to_dict()
    
    def get_file_by_name_and_game(self, file_name: str, game_name: str) -> Optional[FileMetaData]:
        docs = self.collection.where("fileName", "==", file_name).where("gameName", "==", game_name).stream()
        for doc in docs:
            return FileMetaData(**doc.to_dict())
        return None
    
    def update_metadata_last_updated(self, fielf_id: str, ts: datetime) -> None:
        doc_ref = self.collection.document(fielf_id)
        doc_ref.update({"lastUpdatedAt": ts})

    def delete_file(self, fileId: str, logs_service: LogServices) -> Dict:
        doc_ref = self.collection.document(fileId)
        if not doc_ref.get().exists:
            return {"error": "File not found"}
        logs = logs_service.collection.where("fileId", "==", fileId).stream()
        for log_doc in logs:
            logs_service.delete_log(log_doc.id)
        doc_ref.delete()
        return {"message": "File deleted successfully"}

    def update_file(
        self, fileId: str, file: FileMetaData, updatedBy: str, logs_service: LogServices
    ) -> Dict:
        doc_ref = self.collection.document(fileId)
        if not doc_ref.get().exists:
            return {"error": "File not found"}
        update_data = file.dict(exclude={"fileId"}, exclude_none=True)
        doc_ref.update(update_data)
        log = Logs(fileId=fileId, updatedBy=updatedBy)
        logs_service.create_log(log)
        return {"message": "File updated successfully"}



fileServices = FileServices(db)
