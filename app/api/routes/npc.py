from fastapi import APIRouter
from typing import List, Dict
from app.core.services.npcServices import npcServices
from app.core.schema.npcSchema import NpcModel



npcRouter = APIRouter(
    prefix="/files",
    tags=["npc"]
)

@npcRouter.get("/npc")
def get_npcs() -> List[Dict]:
    npcs = npcServices.list_npcs();
    return npcs

@npcRouter.post("/npc")
def create_npc(npc: NpcModel) -> Dict:
    return npcServices.create_npc(npc)