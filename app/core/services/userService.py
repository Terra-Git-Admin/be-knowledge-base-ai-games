from google.cloud import firestore
from app.core.schema.userSchema import UserModel
from typing import Dict, Optional

db = firestore.Client(project="aigameschat", database="school-game")

class UserService:
    COLLECTION_NAME = "users"
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)
    

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        docs = self.collection.where("email", "==", email).stream()
        for doc in docs:
            return UserModel(**doc.to_dict())
        return None
    
    def create_user(self, user: UserModel) -> UserModel:
        doc_ref = self.collection.document(user.userId)
        doc_ref.set(user.dict(exclude_none=True))
        # return user.dict(by_alias=True)
        return user
    
    def get_user(self, userId: str) -> UserModel:
        doc_ref = self.collection.document(userId)
        doc = doc_ref.get()
        return doc.to_dict()

userService = UserService(db)