from google.cloud import firestore
from app.core.schema.ChatStateSchema import ChatStateFlow
from typing import Dict, List

db = firestore.Client(project="aigameschat", database="school-game")



class ChatStateFlowServices:
    COLLECTION_NAME = "chatStateFlows"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def createChatFlow(self, chatStateFlow: ChatStateFlow) -> Dict:
        doc_ref = self.collection.document(chatStateFlow.chatFlowId)
        doc_ref.set(chatStateFlow.dict(exclude_none=True))
        return {"success": True, "chatFlowId": chatStateFlow.chatFlowId}
    
    def listChatFlows(self, gameName: str) -> List[dict]:
        doc_ref = self.collection.where("gameName", "==", gameName).get()
        return [doc.to_dict() for doc in doc_ref]
    
    def getChatFlow(self, chatFlowId: str) -> dict:
        doc_ref = self.collection.document(chatFlowId).get()
        return doc_ref.to_dict()
    
    def updateChatFlow(self, chatFlowId: str, chatStateFlow: ChatStateFlow) -> Dict:
        try:
            doc_ref = self.collection.document(chatFlowId)
            if not doc_ref.get().exists:
                return {"error": "Chat flow not found"}
            doc_ref.update(chatStateFlow.dict(exclude_none=True))
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    def deleteChatFlow(self, chatFlowId: str) -> Dict:
       try:
            self.collection.document(chatFlowId).delete()
            return {"success": True}
       except Exception as e:
            return {"error": str(e)}

chatStateFlowServices = ChatStateFlowServices(db)