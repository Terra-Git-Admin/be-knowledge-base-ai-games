import io
from google.genai import types
from app.core.storage import GCSStorageService
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
from app.core.schema.fileSchema import FileMetaData
from datetime import datetime
from app.core.schema.logsSchema import Logs

googleStorageService = GCSStorageService("aigameschat-game-data")

def upload_files_to_gemini(game_id: str):
    print("Starting Gemini upload job...")

    try:
        # 1️⃣ List all files for the game
        files = googleStorageService.list_files(game_id)

        for file_name in files:
            # 2️⃣ Read each file content
            data = googleStorageService.read_file(f"{game_id}/{file_name}")

            # 3️⃣ Upload to Gemini
            gemini_file = googleStorageService.genai_client.files.upload(
                file=io.BytesIO(data.encode("utf-8")),
                config=types.UploadFileConfig(
                    mime_type="text/plain",
                    display_name=file_name
                ),
            )
            file_doc = fileServices.collection.where("filePath", "==", f"{game_id}/{file_name}").limit(1).get()
            if not file_doc:
                print(f"No metadata found for {file_name}, skipping...")
                continue
            file_id = file_doc[0].id
            update_data = {
            "geminiFileId": gemini_file.name,
            "geminiUploadTime": datetime.utcnow(),
            "lastUpdatedAt": datetime.utcnow(),
        }
            fileServices.collection.document(file_id).update(update_data)

            # 🔒 Step 3: Log the update
            logServices.create_log(
                Logs(fileId=file_id, updatedBy="system_cronjob")
            )
            print(f"Uploaded {file_name} to Gemini: {gemini_file}")

    except Exception as e:
        print("Error in Gemini upload job:", e)