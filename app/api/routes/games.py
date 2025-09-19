from fastapi import APIRouter
from app.core.storage import googleStorageService
# from app.api.routes.filesMeta import seed_missing_etherpad_metadata

gameRouter = APIRouter(
    prefix="/files",
    tags=["Games"]
)

@gameRouter.get("/games")
def get_all_games():
    # seed_missing_etherpad_metadata()
    return googleStorageService.list_games()

@gameRouter.post("/game/create")
def create_game(game_id: str):
    return googleStorageService.create_game(game_id)

@gameRouter.delete("/game/delete")
def delete_game(game_id: str):
    return googleStorageService.delete_game(game_id)