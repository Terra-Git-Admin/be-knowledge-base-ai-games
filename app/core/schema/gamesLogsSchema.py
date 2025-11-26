from pydantic import BaseModel
from typing import Optional


class PromptSchema(BaseModel):
    gameLogId: Optional[str] = None
    files: Optional[list[str]] = None
    isImgUploadPresent: Optional[bool] = None
    prompt: Optional[str] = None
    referencedAssets: Optional[list[str]] = None
    systemPrompt: Optional[str] = None
    temperature: Optional[float] = None
    thinking: Optional[str] = None
    thinkingBudget: Optional[int] = None


class GameLogs(BaseModel):
    prompt: Optional[PromptSchema] = None
    gameTextLog: Optional[str] = None
    response: Optional[str] = None
    timestamp: Optional[str] = None
