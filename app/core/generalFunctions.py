import uuid
import requests
from zoneinfo import ZoneInfo
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

class GeneralFunctions:
    def __init__(self):
        self.gemini_api_key = os.getenv("GENAI_API_KEY")

    def generate_id(self, initials: str) -> str:
        return f"{initials}-{str(uuid.uuid4())}"
    
    def slack_service(self, channel_id: str, message: str):
        url = "https://client-stage.letsterra.com/emails/slack-message"
        payload = {
            "channelName": channel_id,
            "subject": "Notification from Games Dashboard",
            "message": message,
        }
        response = requests.post(url, json=payload, timeout=30)
        try:
            return response.json()
        except ValueError:
            return {"status": response.status_code, "text": response.text or "No response body"}
    
    def send_delete_request_slack(self, delete_queue, channel_id: str):
        local_time = delete_queue.createdAt.astimezone(ZoneInfo("Asia/Kolkata"))
        message = (
                f"User *{delete_queue.createdBy}* has requested deletion of a file.\n\n"
                f"📂 File Name: `{delete_queue.fileName}`\n"
                f"🎮 Game Name: `{delete_queue.gameName}`\n"
                f"📍 Path GCP Bucket: `{delete_queue.filePath}`\n"
                f"🕒 Requested at: {local_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        self.slack_service(channel_id, message)
    def send_cron_failed_details_to_slack(self, failedQueue, channel_id: str):
        if not failedQueue:
            return
        message = (
                f"⚠️ Gemini upload cron completed with *{len(failedQueue)} failed files*.\n"
            )
        self.slack_service(channel_id, message)
    def gemini_upload(self, file_name: str, file_content: str) -> str:
        gemini_upload_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={self.gemini_api_key}"
        
        metadata_payload = {"file": {"display_name": file_name}}
        
            # Structure for multipart/form-data request
        files_payload = {
            'metadata': (None, json.dumps(metadata_payload), 'application/json'),
            'file': (file_name, file_content, 'text/plain'),
        }
        print(f"✅ Calling Gemini REST API to upload '{file_name}'...")
        response = requests.post(gemini_upload_url, files=files_payload, timeout=30)
    
        # This will raise an error for 4xx/5xx responses, which is caught by the except block
        response.raise_for_status() 
    
        response_data = response.json()
        gemini_file_id = response_data['file']['name']
        print(f"✅ Successfully uploaded to Gemini. File ID: {gemini_file_id}")
        return gemini_file_id


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