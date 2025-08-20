# test_gcs.py
from app.core.storage import GCSStorageService

googleStorageService = GCSStorageService("aigameschat-game-data")

BUCKET_NAME = "aigameschat-game-data"

if __name__ == "__main__":
    files = googleStorageService.list_files()
    print("Files in bucket:", files)
