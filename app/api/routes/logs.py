from fastapi import APIRouter
from app.core.services.logService import logServices
from typing import List, Dict


logsRouter = APIRouter(
    prefix="/files",
    tags=["Logs"]
)

@logsRouter.get("/logs/{fileId}")
def get_logs(fileId: str) -> List[Dict]:
    logs = logServices.list_logs(fileId)
    return logs