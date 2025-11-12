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
        # doc_ref = self.collection.document(log.logId)
        # doc_ref.set(log.dict(exclude_none=True))
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
    def delete_all_logs(self, batch_size: int = 500) -> Dict:
        """
        Deletes ALL documents from the top-level /logs collection in batches.
        Recursively continues until the collection is empty.
        """
        try:
            deleted_count = 0

            while True:
                # Fetch limited batch
                docs = list(self.collection.limit(batch_size).stream())
                if not docs:
                    break  # Exit when no docs left

                batch = self.db.batch()
                for doc in docs:
                    batch.delete(doc.reference)
                    deleted_count += 1

                batch.commit()
                print(f"✅ Deleted {deleted_count} logs so far...")

            return {
                "message": f"Deleted {deleted_count} documents from /logs successfully.",
                "deleted_count": deleted_count
            }

        except Exception as e:
            return {"error": str(e)}

logServices = LogServices(db)