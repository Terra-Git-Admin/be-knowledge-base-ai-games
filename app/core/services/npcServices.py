from google.cloud import firestore
from app.core.schema.npcSchema import NpcModel
from typing import List

db = firestore.Client(project="aigameschat", database="school-game")

class NpcServices:
    COLLECTION_NAME = "npcs"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_npc(self, npc: NpcModel):
        doc_ref = self.collection.document(npc.npcId)
        doc_ref.set(npc.dict(exclude_none=True))
        return {
            "message": "Npc created successfully"
        }

    def list_npcs(self) -> List[NpcModel]:
        doc_ref = self.collection.get()
        return [doc.to_dict() for doc in doc_ref]

npcServices = NpcServices(db)