from fastapi import APIRouter, File, Form, UploadFile, Body, HTTPException
from typing import List
from app.core.storage import googleStorageService
from pydantic import BaseModel

class RenameRequest(BaseModel):
    old_path: str
    new_path: str
    username: str

fileRouter = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@fileRouter.get("/", response_model=List[str])
def list_files(game_id: str = ""):
    files = googleStorageService.list_files(game_id)
    print("game_id from lis files", game_id)
    return files

@fileRouter.get("/content")
def get_file_content(path: str):
    print("path for test", path)
    content = googleStorageService.read_file(path)
    return {"filename": path, "content": content}

@fileRouter.post("/upload")
async def upload_file(path: str = Form(...), file: UploadFile = File(...), username: str = Form(...)):
    try:
        content = await file.read()
        googleStorageService.upload_file(path, content.decode("utf-8"), updated_by=username)
        return {"message": "File uploaded successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"error": str(e)}

@fileRouter.put("/update")
def update_file(path: str, content: str = Body(..., embed=True), username: str = Body(..., embed=True), lastSavedRevision: int = Body(..., embed=True)):
    googleStorageService.update_file(path, content, updated_by=username, lastSavedRevision=lastSavedRevision)
    return {"message": "File updated successfully"}

@fileRouter.delete("/delete")
def delete_file(path: str):
    try:
        googleStorageService.delete_file(path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

@fileRouter.post("/rename")
def rename_file(request: RenameRequest):
    try:
        googleStorageService.rename_file(
            request.old_path,
            request.new_path,
            request.username
            )
        return {"message": "File renamed successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"error": str(e)}
