from fastapi import APIRouter, Query
from typing import List, Dict
from app.core.schema.deleteQueue import DeleteQueue
from app.core.services.deleteQueueService import deleteQueueServices
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
deleteQueueRouter = APIRouter(
    prefix="/files",
    tags=["Delete_Queue"]
)

@deleteQueueRouter.get("/deleteQueue", response_model=List[Dict])
def get_delete_queue():
    return deleteQueueServices.get_delete_queue()


@deleteQueueRouter.post("/deleteQueue", response_model=dict)
def create_delete_request(deleteQueue: DeleteQueue):
    return deleteQueueServices.create_delete_request(deleteQueue)


@deleteQueueRouter.delete("/deleteQueue/{requestId}", response_model=dict)
def del_delete_request(requestId: str):
    dq_doc = deleteQueueServices.collection.document(requestId).get()
    if not dq_doc.exists:
        return {"error": "Delete request not found"}
    dq_doc = dq_doc.to_dict()
    fileId = dq_doc.get("fileId")
    createdBy = dq_doc.get("createdBy")
    if not fileId:
        return {"error": "File not found"}
    result = fileServices.update_is_deleted(fileId, True, createdBy, logServices)
    if "error" in result:
        return result
    deleteQueueServices.del_delete_request(requestId)
    return {
        "message": f"File {fileId} marked as deleted and delete request removed"
    }

@deleteQueueRouter.post("/deleteQueue/restore/{fileId}", response_model=dict)
def restore_file(fileId: str, updatedBy: str = Query(...)):
    result = fileServices.update_is_deleted(
        fileId,
        False,
        updatedBy,
        logServices
    )
    return result