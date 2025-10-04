from fastapi import APIRouter
from app.core.services.voiceServices import voiceServices
from typing import List, Dict
from app.core.schema.presetSchema import VoiceModel, PresetModel
from app.core.services.presetServices import presetServices


presetRouter = APIRouter(
    prefix="/files",
    tags=["presets"]
)

@presetRouter.post("/presets/create/voice")
def create_voice(voice: VoiceModel) -> Dict:
    return voiceServices.create_voice(voice)

@presetRouter.get("/presets/list/voices")
def list_voices() -> List[Dict]:
    return voiceServices.list_voices()

@presetRouter.post("/presets/create/preset")
def create_preset(preset: PresetModel) -> Dict:
    return presetServices.create_preset(preset)

@presetRouter.get("/presets/list/presets/{gameName}")
def list_presets(gameName: str) -> List[Dict]:
    return presetServices.list_presets(gameName)

@presetRouter.get("/presets/get/preset/{presetId}")
def get_preset(presetId: str) -> Dict:
    return presetServices.get_preset(presetId)

@presetRouter.delete("/presets/delete/preset/{presetId}")
def delete_preset(presetId: str) -> Dict:
    return presetServices.delete_preset(presetId)

@presetRouter.patch("/presets/update/preset/{presetId}")
def update_preset(presetId: str, preset: PresetModel) -> Dict:
    return presetServices.update_preset(presetId, preset)