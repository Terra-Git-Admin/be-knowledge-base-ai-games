from pydantic import BaseModel, Field
from app.core.generalFunctions import generalFunction
from datetime import datetime

class DeleteQueue(BaseModel):
    requestId: str = Field(default_factory=lambda: generalFunction.generate_id("dq"))
    gameName: str
    fileId: str
    fileName: str
    createdBy: str
    filePath: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
