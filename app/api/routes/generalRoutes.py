from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.services.systemPromptsService import system_prompts_service
from app.core.services.presetServices import presetServices



generalRouter = APIRouter(
    prefix="/files",
    tags=["State Machines"]
)

class PromptRequest(BaseModel):
    gameName: str
    prompt_name: str

class RuntimeConfig(BaseModel):
    gameName: str
    chat_setup_so: List[str]

class RuntimeConfigPresets(BaseModel):
    gameName: str
    preset_so: List[str]

@generalRouter.post("/chat-setup-so/system-prompts")
def get_system_prompt_by_name(request: PromptRequest):
    """
    Get a specific system prompt for a specific game
    """
    try:
        return system_prompts_service.get_system_prompt_by_name(request.gameName, request.prompt_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generalRouter.post("/chat-setup-so/runtime-config")
def get_all_mentioned_chat_setup_so(request: RuntimeConfig):
    """
    Get all mentioned chat setup for a specific game
    """
    counter = 0
    run_time_config:  Dict[str, Any] = {}
    try:
        for setup_so in request.chat_setup_so:
            result = system_prompts_service.get_system_prompt_by_name(request.gameName, setup_so)
            run_time_config[setup_so] = result
            counter += 1
        return {
            "gameName": request.gameName,
            "runtimeConfig": run_time_config,
            "message": f"Successfully fetched {counter} chat setup so for {request.gameName}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@generalRouter.post("/preset/runtime-config")
def get_all_mentioned_preset_so(request: RuntimeConfigPresets):
    counter = 0
    run_time_config: Dict[str, Any] = {}
    try:
        for setup_so in request.preset_so:
            result = presetServices.get_preset_by_name(request.gameName, setup_so)
            if result:
                run_time_config[setup_so] = result
            else:
                run_time_config[setup_so] = {"error": "Preset not found"}
            counter += 1
        return {
            "gameName": request.gameName,
            "presetConfig": run_time_config,
            "message": f"Successfully fetched {counter} chat setup so for {request.gameName}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))