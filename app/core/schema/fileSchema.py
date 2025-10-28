from pydantic import BaseModel, Field
from datetime import datetime
from app.core.generalFunctions import generalFunction
from typing import Optional

class EtherPadState(BaseModel):
    lastSavedRevision: int = 0
    lastSavedAt: Optional[datetime] = None
    unsaved: bool = False


class FileMetaData(BaseModel):
    fileId: str = Field(default_factory=lambda: generalFunction.generate_id("f"))
    fileName: str
    filePath: Optional[str] = None
    gameName: str
    createdAt: datetime
    lastUpdatedAt: datetime
    raw_preview: Optional[str] = None
    geminiUploadTime: Optional[datetime] = None
    geminiFileId: Optional[str] = None
    publicUrl: Optional[str] = None
    isDeleted: bool = False
    etherpad: Optional[EtherPadState] = Field(default_factory=EtherPadState)