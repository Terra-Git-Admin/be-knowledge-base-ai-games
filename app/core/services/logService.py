from google.cloud import firestore
from app.core.schema.logsSchema import Logs
from typing import Dict, List

db = firestore.Client(project="aigameschat", database="school-game")

class LogServices:
    COLLECTION_NAME = "logs"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_log(self, log: Logs) -> Dict:
        doc_ref = self.collection.document(log.logId)
        doc_ref.set(log.dict(exclude_none=True))
        return {
            "message": "Log created successfully"
        }
    
    def list_logs(self, fileId: str) -> List[Dict]:
        doc_ref = self.collection.where("fileId", "==", fileId).order_by("createdAt").stream()
        return [doc.to_dict() for doc in doc_ref]
    
    def delete_log(self, logId: str) -> Dict:
        doc_ref = self.collection.document(logId)
        doc_ref.delete()
        return {
            "message": "Log deleted successfully"
        }

logServices = LogServices(db)