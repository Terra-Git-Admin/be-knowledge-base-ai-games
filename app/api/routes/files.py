from fastapi import APIRouter, File, Form, UploadFile, Body, HTTPException
from typing import List
from app.core.storage import googleStorageService
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import base64

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
    content = googleStorageService.read_file(path)
    if path.endswith((".txt", ".json", ".csv", ".md", ".py", ".xml", ".yml", ".yaml")):
        return {"filename": path, "content": content}
    elif path.endswith((".pdf", ".png", ".jpg", ".jpeg", ".gif")):
        encoded = base64.b64encode(content).decode("utf-8")
        return JSONResponse(content={"filename": path, "content": encoded})
    else:
        encoded = base64.b64encode(content).decode("utf-8")
        return JSONResponse(content={"filename": path, "content": encoded})

@fileRouter.post("/upload")
async def upload_file(path: str = Form(...), file: UploadFile = File(...), username: str = Form(...), fileId: str = Form(None)):
    try:
        content = await file.read()
        googleStorageService.upload_file(file_path = path, file_content = content.decode("utf-8"), updated_by=username, file_id=fileId)
        return {"message": "File uploaded successfully"}
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"error": str(e)}

@fileRouter.post("/upload-image")
async def upload_image(image_name: str = Form(...), file_path: str = Form(...), game_name: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        googleStorageService.upload_image(
            image_name=image_name,
            file_path=file_path,
            image_source=content,
            game_name=game_name,
            is_base64=False
        )
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

@fileRouter.post("/search/{gameName}")
def search_file_content(gameName: str, search_query: str = Body(..., embed=True)):
    try:
        matching_files = googleStorageService.search_file_content(search_query, gameName)
        return matching_files
    except Exception as e:
        return {"error": str(e)}
