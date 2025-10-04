from google.cloud import firestore
from app.core.schema.presetSchema import PresetModel
from typing import Dict, List
from app.core.services.voiceServices import voiceServices


db = firestore.Client(project="aigameschat", database="school-game")

class PresetServices:
    COLLECTION_NAME = "presets"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    def create_preset(self, preset: PresetModel):
        self.collection.document(preset.presetId).set(preset.dict())
        return {
            "message": "Preset created successfully"
        }
    
    def list_presets(self, gameName: str):
        presets = []
        docs = self.collection.where("gameName", "==", gameName).get()
        for doc in docs:
            presets.append(doc.to_dict())
        return presets
    
    def get_preset(self, presetId: str):
        doc = self.collection.document(presetId).get()
        return doc.to_dict() if doc.exists else None
    
    def delete_preset(self, presetId: str):
        self.collection.document(presetId).delete()
        return {
            "message": "Preset deleted successfully"
        }
    
    def update_preset(self, presetId: str, preset: PresetModel):
        update_data = preset.model_dump(exclude_none=True, exclude={"presetId"})
        self.collection.document(presetId).update(update_data)
        return {
            "message": "Preset updated successfully"
        }

presetServices = PresetServices(db)