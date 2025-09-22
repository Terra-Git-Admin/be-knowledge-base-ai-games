from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GameRuntime(BaseModel):
    id: Optional[str] = None
    gameName: str

    class Config:
        from_attributes = True


class CreateGameRequest(BaseModel):
    gameName: str


class GameRuntimeResponse(BaseModel):
    id: str
    gameName: str

    class Config:
        from_attributes = True
