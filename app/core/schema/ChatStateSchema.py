from pydantic import BaseModel, Field
from typing import List, Optional
from app.core.generalFunctions import generalFunction


class DynamicField(BaseModel):
    stateName: str
    promptFile: str
class ChatStateFlow(BaseModel):
    chatFlowId: str = Field(default_factory=lambda: generalFunction.generate_id("ch"))
    chatStateName: str
    flowFile: Optional[str] = None
    states: Optional[List[DynamicField]] = Field(default_factory=list)
    gameName: str