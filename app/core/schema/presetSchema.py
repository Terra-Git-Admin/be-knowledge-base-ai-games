from pydantic import BaseModel, Field
from app.core.generalFunctions import generalFunction
from typing import Optional

class VoiceModel(BaseModel):
    voiceId: str = Field(default_factory=lambda: generalFunction.generate_id("v"))
    voiceName: str
    gender: str
    description: str
    temperature: Optional[float] = None
    pitch: Optional[float] = None
    speedRate: Optional[float] = None
    speechRate: Optional[float] = None

class PresetVoiceModel(BaseModel):
    voiceName: str
    gender: str
    description: str
    temperature: Optional[float] = None
    pitch: Optional[float] = None
    # speedRate: Optional[float] = None
    speechRate: Optional[float] = None

class PresetModel(BaseModel):
    presetId: str = Field(default_factory=lambda: generalFunction.generate_id("pre"))
    presetName: str
    voice: PresetVoiceModel
    gameName: str