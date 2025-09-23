import os
from google.cloud import firestore
from typing import List, Dict, Any, Optional
from datetime import datetime

db = firestore.Client(project="aigameschat", database="school-game")


class SystemPromptsService:
    COLLECTION_NAME = "games-runtime"
    SUBCOLLECTION_NAME = "system-prompts"

    def __init__(self, db_client: firestore.Client):
        self.db = db_client

    def get_all_system_prompts(self, game_name: str) -> List[Dict[str, Any]]:
        """
        Retrieve all system prompts for a specific game
        """
        try:
            subcollection_ref = self.db.collection(self.COLLECTION_NAME).document(game_name).collection(self.SUBCOLLECTION_NAME)
            docs = subcollection_ref.stream()
            system_prompts = []
            
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data['id'] = doc.id
                system_prompts.append(prompt_data)
            
            return system_prompts
        except Exception as e:
            raise Exception(f"Error fetching system prompts: {str(e)}")

    def create_system_prompt(self, game_name: str, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new system prompt for a specific game
        """
        try:
            now = datetime.utcnow()
            prompt_data.update({
                'createdAt': now,
                'updatedAt': now
            })
            
            subcollection_ref = self.db.collection(self.COLLECTION_NAME).document(game_name).collection(self.SUBCOLLECTION_NAME)
            doc_ref = subcollection_ref.add(prompt_data)
            
            prompt_data['id'] = doc_ref[1].id
            return prompt_data
        except Exception as e:
            raise Exception(f"Error creating system prompt: {str(e)}")

    def update_system_prompt(self, game_name: str, prompt_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing system prompt
        """
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            doc_ref = self.db.collection(self.COLLECTION_NAME).document(game_name).collection(self.SUBCOLLECTION_NAME).document(prompt_id)
            doc_ref.update(update_data)
            
            # Get updated document
            updated_doc = doc_ref.get()
            if updated_doc.exists:
                result = updated_doc.to_dict()
                result['id'] = updated_doc.id
                return result
            else:
                raise Exception("System prompt not found")
        except Exception as e:
            raise Exception(f"Error updating system prompt: {str(e)}")


# Create a singleton instance
system_prompts_service = SystemPromptsService(db)
