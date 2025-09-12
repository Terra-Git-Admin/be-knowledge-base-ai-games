import os
from fastapi import FastAPI
from google.cloud import firestore
from app.core.schema.fileSchema import FileMetaData
from app.core.services.logService import LogServices
from app.core.schema.logsSchema import Logs
from typing import Dict, List, Optional
from datetime import datetime
from app.core.services.logService import LogServices
from collections import defaultdict

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
        existing = self.collection.where("filePath", "==", file.filePath).limit(1).stream()
        if any(existing):
            return {"error": "File already exists"}
        if doc_ref.get().exists:
            return {"error": "File already exists"}
        doc_ref.set(file.dict(exclude_none=True))
        log = Logs(fileId=file.fileId, updatedBy=updatedBy)
        logs_service.create_log(log)
        return {"message": "File created successfully"}
    
    def list_files_archive(self, isDeleted: bool ) -> List[Dict]:
        print("🔥 Entered list_files_archive with isDeleted =", isDeleted, type(isDeleted))
        query = self.collection.where("isDeleted", "==", isDeleted)
        docs = query.stream()
        docs_list = []
        for doc in docs:
            doc_data = doc.to_dict()
            print(f"doc id: {doc.id}, data: {doc_data}")
            docs_list.append(doc_data)

        print("total docs fetched:", len(docs_list))
        return docs_list

    def list_files(self, gameName: str ) -> List[FileMetaData]:
        query = self.collection.where("gameName", "==", gameName).where("isDeleted", "==", False)
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
    def update_is_deleted(
    self, fileId: str, isDeleted: bool, updatedBy: str, logs_service: LogServices
) -> Dict:
        from app.core.storage import googleStorageService

        doc_ref = self.collection.document(fileId)
        doc_snapshot = doc_ref.get()

        if not doc_snapshot.exists:
            return {"error": "File not found"}

        existing_data = doc_snapshot.to_dict()
        current_name = existing_data.get("fileName", "")
        current_path = existing_data.get("filePath", "")

        # 🔑 Split filename into name + extension
        base, ext = os.path.splitext(current_name)

        if isDeleted:
            if not base.endswith("_archived"):
                new_name = f"{base}_archived{ext}"
            else:
                new_name = current_name
        else:
            if base.endswith("_archived"):
                new_name = f"{base[:-9]}{ext}"   # remove "_archived"
            else:
                new_name = current_name  # already restored

        # Build new path
        path_parts = current_path.split("/")
        path_parts[-1] = new_name
        new_path = "/".join(path_parts)

        # ✅ Only rename if path changed
        if new_path != current_path:
            googleStorageService.rename_file(
                old_path=current_path,
                new_path=new_path,
                username=updatedBy
            )

        # Always update Firestore
        self.collection.document(fileId).update({
            "isDeleted": isDeleted,
            "lastUpdatedAt": datetime.utcnow(),
            "fileName": new_name,
            "filePath": new_path,
        })

        # Add log
        log = Logs(fileId=fileId, updatedBy=updatedBy)
        logs_service.create_log(log)

        return {"message": f"File {'archived' if isDeleted else 'restored'} successfully"}


    
    def delete_dups(self):
        docs = self.collection.stream()
        grouped = defaultdict(list)
        for doc in docs:
            data = doc.to_dict()
            file_path = data.get("filePath")
            if file_path:
                grouped[file_path].append((doc.id, data))
        deleted_count = 0

        for file_path, items in grouped.items():
            if len(items) > 1:
                print(f"⚠️ Duplicate found for {file_path}, count={len(items)}")

                items.sort(key=lambda x: x[1].get("createdAt"))

                # First one = keeper
                keeper = items[0]
                duplicates = items[1:]

                for dup in duplicates:
                    self.collection.document(dup[0]).delete()
                    deleted_count += 1
                    print(f"🗑️ Deleted duplicate: {dup[0]} for {file_path}")

        print(f"✅ Finished. Deleted {deleted_count} duplicates.")
    
    def addField(self):
        files_ref = self.collection.stream()
        batch = self.db.batch()
        for file in files_ref:
            if "isDeleted" not in file.to_dict():
                batch.update(file.reference, {"isDeleted": False})
        batch.commit()



fileServices = FileServices(db)
