from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DynamicField(BaseModel):
    label: str
    placeholder: str

class SystemPromptResponse(BaseModel):
    id: str
    systemPromptFileId: str
    knowledgeBase: List[str]
    dynamics: List[DynamicField]
    outputFilename: str
    instructions: str
    createdAt: datetime
    updatedAt: datetime

class CreateSystemPromptRequest(BaseModel):
    systemPromptFileId: str
    knowledgeBase: List[str]
    dynamics: List[DynamicField]
    outputFilename: str
    instructions: Optional[str] = None

class UpdateSystemPromptRequest(BaseModel):
    systemPromptFileId: Optional[str] = None
    knowledgeBase: Optional[List[str]] = None
    dynamics: Optional[List[DynamicField]] = None
    outputFilename: Optional[str] = None
    instructions: Optional[str] = None
