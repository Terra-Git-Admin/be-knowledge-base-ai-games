from pydantic import BaseModel, Field, EmailStr
from app.core.generalFunctions import generalFunction

class UserModel(BaseModel):
    userId: str = Field(default_factory=lambda: generalFunction.generate_id("u"))
    username: str
    email: EmailStr