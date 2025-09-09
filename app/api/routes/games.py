from fastapi import APIRouter
from app.core.storage import googleStorageService

gameRouter = APIRouter(
    prefix="/files",
    tags=["Games"]
)

@gameRouter.get("/games")
def get_all_games():
    return googleStorageService.list_games()

@gameRouter.post("/game/create")
def create_game(game_id: str):
    return googleStorageService.create_game(game_id)

@gameRouter.delete("/game/delete")
def delete_game(game_id: str):
    return googleStorageService.delete_game(game_id)