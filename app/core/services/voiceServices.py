from google.cloud import firestore
from app.core.schema.presetSchema import VoiceModel
from typing import Dict, List

db = firestore.Client(project="aigameschat", database="school-game")

class VoiceServices:
    COLLECTION_NAME = "voices"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    def create_voice(self, voice: VoiceModel):
        self.collection.document(voice.voiceId).set(voice.model_dump())
        return voice.model_dump() 
    
    def list_voices(self):
        docs = self.collection.get()
        return [doc.to_dict() for doc in docs]
    
    def get_voice(self, voiceId: str):
        doc_ref = self.collection.document(voiceId)
        doc = doc_ref.get()
        return doc.to_dict()
    
    def delete_voice(self, voiceId: str):
        doc_ref = self.collection.document(voiceId)
        doc_ref.delete()
        return {"message": "Voice deleted successfully"}
    
    def update_voice(self, voiceId: str, voice: VoiceModel):
        update_data = voice.model_dump(exclude_none=True)
        self.collection.document(voiceId).update(update_data)
        return update_data 

voiceServices = VoiceServices(db)