from fastapi import APIRouter, File, Form, UploadFile, Body
from typing import List
from app.core.storage import googleStorageService

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
        googleStorageService.upload_file(path, content, updated_by=username)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@fileRouter.put("/update")
def update_file(path: str, content: str = Body(..., embed=True), username: str = Body(..., embed=True)):
    googleStorageService.update_file(path, content, updated_by=username)
    return {"message": "File updated successfully"}

@fileRouter.delete("/delete")
def delete_file(path: str):
    try:
        googleStorageService.delete_file(path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}
