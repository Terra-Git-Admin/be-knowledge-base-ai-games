from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.services.systemPromptsService import system_prompts_service



generalRouter = APIRouter(
    prefix="/files",
    tags=["chat setup so"]
)

class PromptRequest(BaseModel):
    gameName: str
    prompt_name: str

class RuntimeConfig(BaseModel):
    gameName: str
    chat_setup_so: List[str]

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