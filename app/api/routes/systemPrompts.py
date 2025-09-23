from fastapi import APIRouter, HTTPException
from app.core.services.systemPromptsService import system_prompts_service
from app.core.schema.systemPromptsSchema import SystemPromptResponse, CreateSystemPromptRequest, UpdateSystemPromptRequest
from typing import List

systemPromptsRouter = APIRouter(
    prefix="/{gameName}/system-prompts",
    tags=["System Prompts"]
)

@systemPromptsRouter.get("/", response_model=List[SystemPromptResponse])
def get_all_system_prompts(gameName: str):
    """
    Get all system prompts for a specific game
    """
    try:
        prompts = system_prompts_service.get_all_system_prompts(gameName)
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@systemPromptsRouter.post("/", response_model=SystemPromptResponse)
def create_system_prompt(gameName: str, request: CreateSystemPromptRequest):
    """
    Create a new system prompt for a specific game
    """
    try:
        prompt_data = request.dict()
        prompt = system_prompts_service.create_system_prompt(gameName, prompt_data)
        return prompt
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@systemPromptsRouter.put("/{promptId}", response_model=SystemPromptResponse)
def update_system_prompt(gameName: str, promptId: str, request: UpdateSystemPromptRequest):
    """
    Update an existing system prompt
    """
    try:
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        prompt = system_prompts_service.update_system_prompt(gameName, promptId, update_data)
        return prompt
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
