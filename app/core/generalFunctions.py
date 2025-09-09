import uuid
import requests
from zoneinfo import ZoneInfo
from datetime import datetime

class GeneralFunctions:
    def __init__(self):
        pass
    def generate_id(self, initials: str) -> str:
        return f"{initials}-{str(uuid.uuid4())}"
    
    def send_delete_request_slack(self, delete_queue, channel_id: str):
        url = "https://client-stage.letsterra.com/emails/slack-message"
        local_time = delete_queue.createdAt.astimezone(ZoneInfo("Asia/Kolkata"))
        subject = f"🗑️ Delete Request for {delete_queue.fileName}"
        message = (
            f"User *{delete_queue.createdBy}* has requested deletion of a file.\n\n"
            f"📂 File Name: `{delete_queue.fileName}`\n"
            f"🎮 Game Name: `{delete_queue.gameName}`\n"
            f"📍 Path GCP Bucket: `{delete_queue.filePath}`\n"
            f"🕒 Requested at: {local_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        payload = {
        "channelName": channel_id,
        "subject": subject,
        "message": message,
    }
        response = requests.post(url, json=payload)
        try:
            return response.json()
        except ValueError:
            return {"status": response.status_code, "text": response.text or "No response body"}

generalFunction = GeneralFunctions()

# def seed_files_metadata(
#     gcs_service: GCSStorageService,
#     file_service,
#     logs_service,
#     preview_length: int = 200
# ):
#     """
#     Iterate through all files in GCS and populate Firestore metadata.
#     """
#     files = gcs_service.list_files("")  # no prefix = all files
#     print(f"📂 Found {len(files)} files in GCS")

#     for file_path in files:
#         try:
#             # Split path into gameName and fileName
#             # parts = file_path.split("/", 1)
#             file_name = file_path.rsplit("/", 1)[-1]
#             # if len(parts) == 1:
#             #     game_name, file_name = "default", parts[0]
#             # else:
#             #     game_name, file_name = parts[0], parts[1]

#             # ✅ Get file content
#             content = gcs_service.read_file(file_path)

#             # ✅ Raw preview (first 200 chars)
#             preview = content[:preview_length]

#             # ✅ Create metadata
#             metadata = FileMetaData(
#                 fileName=file_name,
#                 gameName="school-game",
#                 createdAt=datetime.utcnow(),
#                 lastUpdatedAt=datetime.utcnow(),
#                 raw_preview=preview,
#             )

#             # ✅ Insert into Firestore (skip if exists)
#             result = file_service.create_file(metadata, updatedBy="system_seed", logs_service=logs_service)
#             print(f"✅ {file_path} → {result}")

#         except Exception as e:
#             print(f"❌ Failed {file_path}: {e}")