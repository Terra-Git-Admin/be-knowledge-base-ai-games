import os
from app.core.storage import GCSStorageService
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
from datetime import datetime
from app.core.schema.logsSchema import Logs
from app.core.generalFunctions import generalFunction
import time
import mimetypes

googleStorageService = GCSStorageService("aigameschat-game-data")

ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

MAX_RETRIES = 3
RETRY_DELAY = 5

# def upload_files_to_gemini(game_id: str):
#     print("Starting Gemini upload job...")

#     # 1️⃣ List all files for the game
#     channel_id = "shivandru-self-dm" if ENVIRONMENT == "dev" else "games-production"
#     try:
#         files_meta = fileServices.list_files(game_id)
#     except Exception as e:
#         print(f"❌ Failed to list files for game {game_id}: {e}")
#         return
#     failed_files = []
#     for meta in files_meta:
#         path_name = meta["filePath"]
#         file_name = path_name.split("/")[-1]

#         try:
#             # 2️⃣ Read file content
#             data = googleStorageService.read_file(path_name)
#         except Exception as e:
#             print(f"❌ Failed to read {file_name}: {e}")
#             continue

#         gemini_file_id = None
#         for attempt in range(1, MAX_RETRIES + 1):
#             try:
#                 print(f"⏳ Uploading {file_name} (attempt {attempt}/{MAX_RETRIES})...")
#                 gemini_file_id = generalFunction.gemini_upload(
#                     file_name=file_name, file_content=data
#                 )
#                 print(f"✅ Uploaded {file_name} to Gemini: {gemini_file_id}")
#                 break  # success → exit retry loop
#             except Exception as e:
#                 print(f"⚠️ Attempt {attempt} failed for {file_name}: {e}")
#                 if attempt < MAX_RETRIES:
#                     time.sleep(RETRY_DELAY)
#                 else:
#                     failed_files.append(file_name)
#                     print(f"❌ All retries failed for {file_name}, skipping...")
        
#         if not gemini_file_id:
#             continue  # go to next file without crashing

#         try:
#             # 3️⃣ Update Firestore
#             file_doc = fileServices.collection.where("filePath", "==", path_name).limit(1).get()
#             if not file_doc:
#                 print(f"⚠️ No metadata found for {file_name}, skipping update...")
#                 continue

#             file_id = file_doc[0].id
#             update_data = {
#                 "geminiFileId": gemini_file_id,
#                 "geminiUploadTime": datetime.utcnow(),
#                 "lastUpdatedAt": datetime.utcnow(),
#             }
#             fileServices.collection.document(file_id).update(update_data)

#             # 4️⃣ Log the update
#             logServices.create_log(
#                 Logs(fileId=file_id, updatedBy="system_cronjob")
#             )
#             print(f"📝 Metadata updated for {file_name}")

#         except Exception as e:
#             print(f"❌ Failed to update DB/logs for {file_name}: {e}")
#     if failed_files:
#         print(f"❌ Failed to upload files: {', '.join(failed_files)}")
#         generalFunction.send_cron_failed_details_to_slack(failed_files, channel_id)


def upload_files_to_gemini(game_id: str):
    print("🚀 Starting Gemini upload job...")

    channel_id = "shivandru-self-dm" if ENVIRONMENT == "dev" else "games-production"

    try:
        files_meta = fileServices.list_files(game_id)
    except Exception as e:
        print(f"❌ Failed to list files for game {game_id}: {e}")
        return

    failed_files = []

    for meta in files_meta:
        path_name = meta.get("filePath")
        if not path_name:
            print("⚠️ Skipping file with no path")
            continue

        file_name = path_name.split("/")[-1]
        mime_type, _ = mimetypes.guess_type(file_name)
        mime_type = mime_type or "application/octet-stream"

        try:
            data = googleStorageService.read_file(path_name)
        except Exception as e:
            print(f"❌ Failed to read {file_name}: {e}")
            continue

        gemini_file_id = None

        # Try multiple times (for resilience)
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                print(f"⏳ Uploading {file_name} (attempt {attempt}/{MAX_RETRIES})...")
                
                # 📝 TEXT FILES (.txt, .md, .json, etc.)
                if mime_type.startswith("text/") or file_name.lower().endswith((".md", ".txt", ".json")):
                    if isinstance(data, bytes):
                        data = data.decode("utf-8", errors="ignore")
                    gemini_file_id = generalFunction.gemini_upload(
                        file_name=file_name,
                        file_content=data
                    )

                # 🖼️ IMAGE FILES (jpg, png, gif, etc.)
                elif mime_type.startswith("image/"):
                    gemini_file_id = generalFunction.gemini_image_upload(
                        image_name=file_name,
                        image_source=data,
                        is_base64=False
                    )

                # 📄 PDF FILES (treat as file upload, not image)
                elif mime_type == "application/pdf":
                    gemini_file_id = generalFunction.gemini_upload(
                        file_name=file_name,
                        file_content=data
                    )

                # 🧩 UNKNOWN FILE TYPES
                else:
                    print(f"⚠️ Unsupported MIME type ({mime_type}), uploading as binary fallback")
                    if isinstance(data, bytes):
                        try:
                            data = data.decode("utf-8")
                        except Exception:
                            pass
                    gemini_file_id = generalFunction.gemini_upload(
                        file_name=file_name,
                        file_content=data
                    )

                print(f"✅ Uploaded {file_name} to Gemini: {gemini_file_id}")
                break

            except Exception as e:
                print(f"⚠️ Attempt {attempt} failed for {file_name}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    failed_files.append(file_name)
                    print(f"❌ All retries failed for {file_name}, skipping...")

        if not gemini_file_id:
            continue

        # 🔄 Update Firestore metadata and logs
        try:
            file_doc = fileServices.collection.where("filePath", "==", path_name).limit(1).get()
            if not file_doc:
                print(f"⚠️ No metadata found for {file_name}, skipping update...")
                continue

            file_id = file_doc[0].id
            update_data = {
                "geminiFileId": gemini_file_id,
                "geminiUploadTime": datetime.utcnow(),
                "lastUpdatedAt": datetime.utcnow(),
            }
            fileServices.collection.document(file_id).update(update_data)

            logServices.create_log(Logs(fileId=file_id, updatedBy="system_cronjob"))
            print(f"📝 Metadata updated for {file_name}")

        except Exception as e:
            print(f"❌ Failed to update DB/logs for {file_name}: {e}")

    # 🧾 Summary report
    if failed_files:
        print(f"❌ Failed to upload files: {', '.join(failed_files)}")
        generalFunction.send_cron_failed_details_to_slack(failed_files, channel_id)
    else:
        print("✅ All files uploaded successfully!")