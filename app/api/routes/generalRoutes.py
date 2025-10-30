from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.services.systemPromptsService import system_prompts_service



generalRouter = APIRouter(
    prefix="/files",
    tags=["chat setup so"]
)

class PromptRequest(BaseModel):
    gameName: str
    prompt_name: str

@generalRouter.post("/chat-setup-so/system-prompts")
def get_system_prompt_by_name(request: PromptRequest):
    """
    Get a specific system prompt for a specific game
    """
    try:
        print(f"Querying title == '{request.prompt_name}'")
        return system_prompts_service.get_system_prompt_by_name(request.gameName, request.prompt_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))