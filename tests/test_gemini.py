from pathlib import Path
import os
from app.core.generalFunctions import generalFunction

generalFunction.gemini_api_key = os.getenv("GENAI_API_KEY")

image_name = "test.png"
image_path = str(Path(__file__).parent / "test.png")

try:
    gemini_file_id = generalFunction.gemini_image_upload(image_name, image_path)
    print("✅ Test successful! Gemini File ID:", gemini_file_id)
except Exception as e:
    print("❌ Upload failed:", e)