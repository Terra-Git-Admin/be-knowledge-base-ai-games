from typing import List
from fastapi import FastAPI, UploadFile, File, Body
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
def list_files(prefix: str = "school-game/knowledge-base/"):
    files = googleStorageService.list_files(prefix)
    return [f.split("/")[-1] for f in files]

@app.get("/files/{file_name}")
def get_file_content(file_name: str):
    content = googleStorageService.read_file(file_name)
    return {"filename": file_name, "content": content}

@app.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        googleStorageService.upload_file(file.filename, content)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.put("/files/update/{file_name}")
def update_file(file_name: str, content: str = Body(..., embed=True)):
    googleStorageService.update_file(file_name, content)
    return {"message": "File updated successfully"}

@app.delete("/files/delete/{file_name}")
def delete_file(file_name: str):
    try:
        googleStorageService.delete_file(file_name)
        return {"message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}