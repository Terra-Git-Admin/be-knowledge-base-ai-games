from fastapi import APIRouter, Query
from app.core.services.fileService import fileServices
# from app.core.services.fileService import fileServices
from app.core.services.etherPadService import etherpadService

filesMetaRouter = APIRouter(
    prefix="/files",
    tags=["Files_Meta_Data"]
)

# def seed_missing_etherpad_metadata():
#     files = fileServices.collection.stream()
#     for doc in files:
#         data = doc.to_dict()
#         print("doc from firestore", data)
#         if "etherpad" in data:
#             pad_id = data.get("fileId")
#             if not pad_id:
#                 continue  # skip files that aren’t linked to a pad

#             try:
#                 rev_info = etherpadService.getRevisionCount(pad_id)
#                 latest_rev = rev_info["etherpad"]["lastSavedRevision"]

#                 update_data = {
#                     "etherpad.lastSavedRevision": latest_rev,
#                     "etherpad.lastSavedAt": None,
#                     "etherpad.unsaved": False,
#                 }
#                 fileServices.collection.document(doc.id).update(update_data)
#                 print(f"Seeded etherpad metadata for {doc.id}")

#             except Exception as e:
#                 print(f"Failed to seed {doc.id}: {e}")

@filesMetaRouter.get("/meta/{gameName}")
def list_meta(gameName: str):
    files = fileServices.list_files(gameName)
    print("meta data files from meta List", files)
    # seed_missing_etherpad_metadata()
    return files

@filesMetaRouter.get("/meta/archive/")
def list_meta_archive(isDeleted: bool = Query(True, description="Filter by deletion status")):
    files = fileServices.list_files_archive(isDeleted = isDeleted)
    print("meta data files", files)
    return files