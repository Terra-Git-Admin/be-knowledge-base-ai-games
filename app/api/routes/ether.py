from fastapi import APIRouter
from pydantic import BaseModel
from app.core.services.etherPadService import etherpadService


etherRouter = APIRouter(
    prefix="/files",
    tags=["Ether"]
)

class CreatePadRequest(BaseModel):
    pad_id: str
    initialContent: str = ""

@etherRouter.post("/ether/create", response_model=dict)
def create_ether_pad(req: CreatePadRequest):
    return etherpadService.openFileInEtherpad(req.pad_id, req.initialContent)

@etherRouter.get("/ether/{pad_id}", response_model=str)
def get_ether_pad(pad_id: str):
    return etherpadService.getPadContent(pad_id)