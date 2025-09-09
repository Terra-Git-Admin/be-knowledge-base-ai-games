import os
from google.cloud import firestore
from app.core.schema.deleteQueue import DeleteQueue
from typing import List, Dict
from app.core.generalFunctions import generalFunction

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

class DeleteQueueServices:
    COLLECTION_NAME = "deleteQueue"
    CHANNEL = "shivandru-self-dm" if ENVIRONMENT == "dev" else "games-production"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def get_delete_queue(self) -> List[Dict]:
        docs = self.collection.stream()
        return [doc.to_dict() for doc in docs]
    
    def create_delete_request(self, deleteQueue: DeleteQueue):
        doc_ref = self.collection.document(deleteQueue.requestId)
        doc_ref.set(deleteQueue.dict(exclude_none=True))
        # generalFunction.send_delete_request_slack(deleteQueue, self.CHANNEL)
        return {
            "message": "Delete request created successfully"
        }
    
    def del_delete_request(self, requestId: str):
        doc_ref = self.collection.document(requestId)
        if not doc_ref.get().exists:
            return {"error": "Delete request not found"}
        doc_ref.delete()
        return {
            "message": "Delete request deleted successfully"
        }

db = firestore.Client(project="aigameschat", database="school-game")

deleteQueueServices = DeleteQueueServices(db)

