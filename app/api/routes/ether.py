from fastapi import APIRouter
from pydantic import BaseModel
from app.core.services.etherPadService import etherpadService
from typing import List


etherRouter = APIRouter(
    prefix="/files",
    tags=["Ether"]
)

class CreatePadRequest(BaseModel):
    pad_id: str
    initialContent: str = ""

class GetRevisionRequest(BaseModel):
    pad_ids: List[str]

class PadRevision(BaseModel):
    pad_id: str
    lastSavedRevision: int

class GetRevisionResponse(BaseModel):
    revisions: List[PadRevision]

@etherRouter.post("/ether/create", response_model=dict)
def create_ether_pad(req: CreatePadRequest):
    return etherpadService.openFileInEtherpad(req.pad_id, req.initialContent)

@etherRouter.get("/ether/{pad_id}", response_model=str)
def get_ether_pad(pad_id: str):
    return etherpadService.getPadContent(pad_id)

@etherRouter.post("/ether/revisions")
def get_ether_pad_revision(req: GetRevisionRequest):
    results = []
    for pad_id in req.pad_ids:
        data = etherpadService.getRevisionCount(pad_id)
        # results.append({
        #      "padId": pad_id,
        #     "revisionCount": data.get("revisionCount", 0) if "revisionCount" in data else 0
        # })
        results.append(data)
    print("result from etherpad", results)
    return {"revisions": results}
