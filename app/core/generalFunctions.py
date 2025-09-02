import uuid
class GeneralFunctions:
    def __init__(self):
        pass
    def generate_id(self, initials: str) -> str:
        return f"{initials}-{str(uuid.uuid4())}"

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