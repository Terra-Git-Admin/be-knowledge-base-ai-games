import uuid
import requests
from zoneinfo import ZoneInfo
from datetime import datetime
import json
import base64
import os
from dotenv import load_dotenv
import mimetypes

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
        mime_type, _ = mimetypes.guess_type(file_name)
        # if mime_type is None:
        #     mime_type = "text/plain"
        if file_name.lower().endswith((".txt", ".md", ".json")):
            mime_type = "text/plain"
        elif mime_type is None:
            mime_type = "application/octet-stream"
        
            # Structure for multipart/form-data request
        files_payload = {
            'metadata': (None, json.dumps(metadata_payload), 'application/json'),
            'file': (file_name, file_content, mime_type),
        }
        print(f"✅ Uploading '{file_name}' with MIME type: {mime_type}")
        response = requests.post(gemini_upload_url, files=files_payload, timeout=30)
    
        # This will raise an error for 4xx/5xx responses, which is caught by the except block
        response.raise_for_status() 
    
        response_data = response.json()
        gemini_file_id = response_data['file']['name']
        print(f"✅ Successfully uploaded to Gemini. File ID: {gemini_file_id}")
        return gemini_file_id
    
    def gemini_image_upload(self, image_name: str, image_source: str, is_base64: bool = True):
        gemini_upload_url = f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={self.gemini_api_key}"
        print(f"✅ Calling Gemini REST API to upload '{self.gemini_api_key}'...")
        mime_type, _ = mimetypes.guess_type(image_name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        if is_base64:
            base64_data = image_source.split(",")[-1]
            image_bytes = base64.b64decode(base64_data)
        else:
            if isinstance(image_source, (bytes, bytearray)):
                image_bytes = image_source
            else:
                raise TypeError(f"Expected bytes for image_source when is_base64=False, got {type(image_source)}")
        metadata_payload = {"file": {"display_name": image_name}}
        files_payload = {
        'metadata': (None, json.dumps(metadata_payload), 'application/json'),
        'file': (image_name, image_bytes, mime_type),
    }

        print(f"📤 Uploading image '{image_name}' to Gemini...")
        response = requests.post(gemini_upload_url, files=files_payload, timeout=30)
        response.raise_for_status()

        data = response.json()
        gemini_file_id = data["file"]["name"]

        print(f"✅ Uploaded successfully to Gemini. File ID: {gemini_file_id}")
        return gemini_file_id


generalFunction = GeneralFunctions()