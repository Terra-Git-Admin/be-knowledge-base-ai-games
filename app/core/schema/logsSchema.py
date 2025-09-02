from pydantic import BaseModel, Field
from datetime import datetime
from app.core.generalFunctions import generalFunction


class Logs(BaseModel):
    logId: str = Field(default_factory=lambda: generalFunction.generate_id("l"))
    fileId: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedBy: str