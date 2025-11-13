from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from app.core.services.systemPromptsService import system_prompts_service
from app.core.services.presetServices import presetServices
from app.core.services.gameLogsServices import gameLogsServices



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



@generalRouter.get("/debug/logs")
def get_all_logs(
    game_name: str | None = Query(None, description="Optional game name filter"),
    username: str | None = Query(None, description="Optional username filter"),
    limit: int = Query(20, description="Limit the number of logs returned"),
    page: int = Query(0, description="Page number for pagination (starts at 0)"),
):
    """
    Returns all logs across players/games, optionally filtered by game or player.
    Example: /debug/logs?game_name=debug-companions
    """
    try:
        offset = page * limit
        return gameLogsServices.get_all_logs(game_name=game_name, username=username, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@generalRouter.get("/debug/logs/by-path")
def get_log_by_path(log_path: str = Query(..., description="Full Firestore path of the log")):
    """
    Fetch a single log's details by its Firestore path.
    Example: /debug/logs/by-path?log_path=players/Arpita/games/Yuki_V2/logs/kOPXuXRdfiDjx9uCLPXe
    """
    try:
        return gameLogsServices.get_log_by_path(log_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@generalRouter.get("/games/by-user")
def get_games_by_user(username: str = Query(...)):
    return gameLogsServices.get_games_for_user(username)

@generalRouter.get("/logs/by-user-game/details")
def get_logs_by_user_game(username: str = Query(...), game_name: str = Query(...)):
    return gameLogsServices.get_logs_for_user_and_game(username, game_name)

@generalRouter.get("/gamenames/debug")
def get_game_names():
    return gameLogsServices.get_all_games()