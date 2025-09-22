from fastapi import APIRouter, HTTPException
from app.core.services.gamesRuntimeService import games_runtime_service
from app.core.schema.gamesRuntimeSchema import GameRuntimeResponse, CreateGameRequest
from typing import List

gamesRuntimeRouter = APIRouter(
    prefix="/games-runtime",
    tags=["Games Runtime"]
)

@gamesRuntimeRouter.get("/", response_model=List[GameRuntimeResponse])
def get_all_runtime_games():
    """
    Get all games from the games-runtime collection
    """
    try:
        games = games_runtime_service.get_all_games()
        return games
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@gamesRuntimeRouter.post("/", response_model=GameRuntimeResponse)
def create_runtime_game(request: CreateGameRequest):
    """
    Create a new game in the games-runtime collection
    """
    try:
        game = games_runtime_service.create_game(request.gameName)
        return game
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
