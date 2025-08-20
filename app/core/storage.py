from google.cloud import storage
from typing import List

class GCSStorageService:
    def __init__(self, bucket_name: str):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
        self.base_prefix = "school-game/knowledge-base/"
    
    def list_files(self, prefix: str = "") -> List[str]:
        try:
            full_prefix = self.base_prefix
            blobs_iter = self.bucket.list_blobs(prefix=full_prefix)
            return [b.name for b in blobs_iter if not b.name.endswith('/')]
        except Exception as e:
            raise RuntimeError(e)

    def read_file(self, file_name: str) -> str:
        try:
            blob = self.bucket.blob(self.base_prefix + file_name)
            return blob.download_as_text()
        except Exception as e:
            raise RuntimeError(e)
    def upload_file(self, file_name: str, file_content: str) -> None:
        try:
            blob = self.bucket.blob(self.base_prefix + file_name)
            blob.upload_from_string(file_content)
        except Exception as e:
            raise RuntimeError(e)
    # def upload_content(self, blob_name: str, content: str) -> None:
    #     pass
    def update_file(self, blob_name: str, content: str) -> None:
        try:
            blob = self.bucket.blob(self.base_prefix + blob_name)
            blob.upload_from_string(content, content_type="text/plain")
        except Exception as e:
            raise RuntimeError(e)
    def delete_file(self, blob_name: str) -> None:
        try:
            blob = self.bucket.blob(self.base_prefix + blob_name)
            blob.delete()
        except Exception as e:
            raise RuntimeError(e)
