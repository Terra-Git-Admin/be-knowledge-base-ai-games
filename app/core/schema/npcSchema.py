from pydantic import BaseModel, Field
from app.core.generalFunctions import generalFunction

class NpcModel(BaseModel):
    npcId: str = Field(default_factory=lambda: generalFunction.generate_id("npc"))
    label: str
    placeholder: str
    gameName: str