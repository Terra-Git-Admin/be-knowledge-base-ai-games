from typing import List
from fastapi import FastAPI, UploadFile, File, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from app.core.storage import GCSStorageService

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

googleStorageService = GCSStorageService("aigameschat-game-data")
@app.get("/")
def root():
    return {"message": "Hello from FastAPI 🚀"}

@app.get("/files", response_model=List[str])
def list_files(game_id: str = ""):
    files = googleStorageService.list_files(game_id)
    print("game_id from lis files", game_id)
    print("files from lis files", files)
    return files

@app.get("/files/content")
def get_file_content(path: str):
    content = googleStorageService.read_file(path)
    return {"filename": path, "content": content}

@app.post("/files/upload")
async def upload_file(path: str = Form(...), file: UploadFile = File(...)):
    try:
        content = await file.read()
        googleStorageService.upload_file(path, content)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.put("/files/update")
def update_file(path: str, content: str = Body(..., embed=True)):
    googleStorageService.update_file(path, content)
    return {"message": "File updated successfully"}

@app.delete("/files/delete")
def delete_file(path: str):
    try:
        googleStorageService.delete_file(path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}