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

    def list_npcs(self, gameName: str) -> List[NpcModel]:
        doc_ref = self.collection.where("gameName", "==", gameName).stream()
        return [doc.to_dict() for doc in doc_ref]
    
    def get_npc(self, npcId: str) -> dict:
        doc_ref = self.collection.document(npcId).get()
        if not doc_ref.exists:
            return {"error": "NPC not found"}
        return doc_ref.to_dict()
    
    def update_npc(self, npcId: str, npc: NpcModel):
        doc_ref = self.collection.document(npcId)
        doc_ref.update(npc.dict(exclude_none=True))
        return {
            "message": "Npc updated successfully"
        }

    def delete_npc(self, npcId: str):
        doc_ref = self.collection.document(npcId)
        if not doc_ref.get().exists:
            return {"error": "Npc not found"}
        doc_ref.delete()
        return {
            "message": "Npc deleted successfully"
        }

npcServices = NpcServices(db)