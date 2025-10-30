from fastapi import APIRouter
from typing import List, Dict
from app.core.services.npcServices import npcServices
from app.core.schema.npcSchema import NpcModel



npcRouter = APIRouter(
    prefix="/files",
    tags=["npc"]
)

@npcRouter.get("/npc/{gameName}")
def get_npcs(gameName: str) -> List[Dict]:
    npcs = npcServices.list_npcs(gameName)
    return npcs

@npcRouter.get("/npc/{npcId}")
def get_npc(npcId: str) -> Dict:
    return npcServices.get_npc(npcId)

@npcRouter.post("/npc")
def create_npc(npc: NpcModel) -> Dict:
    return npcServices.create_npc(npc)

@npcRouter.patch("/npc/update/{npcId}")
def update_npc(npcId: str, npc: NpcModel) -> Dict:
    return npcServices.update_npc(npcId, npc)

@npcRouter.delete("/npc/delete/{npcId}")
def delete_npc(npcId: str) -> Dict:
    return npcServices.delete_npc(npcId)