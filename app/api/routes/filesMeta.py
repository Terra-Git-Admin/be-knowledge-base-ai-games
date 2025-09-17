from fastapi import APIRouter, Query
from app.core.services.fileService import fileServices

filesMetaRouter = APIRouter(
    prefix="/files",
    tags=["Files_Meta_Data"]
)

@filesMetaRouter.get("/meta/{gameName}")
def list_meta(gameName: str):
    files = fileServices.list_files(gameName)
    # fileServices.seed_etherpad_field()
    print("meta data files", files)
    return files

@filesMetaRouter.get("/meta/archive/")
def list_meta_archive(isDeleted: bool = Query(True, description="Filter by deletion status")):
    files = fileServices.list_files_archive(isDeleted = isDeleted)
    print("meta data files", files)
    return files