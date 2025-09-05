from typing import List, Dict
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Body, Form, Request
from fastapi.responses import RedirectResponse
from requests.exceptions import RequestException
from app.auth.google_oauth import oauth
from fastapi.middleware.cors import CORSMiddleware
from app.core.storage import GCSStorageService
from app.core.services.userService import userService
from app.core.schema.userSchema import UserModel
from starlette.middleware.sessions import SessionMiddleware
# from app.core.schema.fileSchema import FileMetaData
from app.core.services.fileService import fileServices
from app.core.services.logService import logServices
# from google import genai
# from google.genai import types
# import io
# import mimetypes
# from google.cloud import storage
from app.core.scheduler.geminiSchedular import start_scheduler, scheduler

# client = genai.Client(
#     api_key = "AIzaSyAO5d-UQflX90uYqkWxppH6Qrasv3WNEpk"
# )

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET_KEY"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
googleStorageService = GCSStorageService("aigameschat-game-data")

# ENVIRONMENT = os.environ["ENVIRONMENT"]
ENVIRONMENT = "prod"

@app.get("/")
def root():
    return {"message": "Hello from FastAPI 🚀"}


@app.on_event("startup")
def on_startup():
    games = googleStorageService.list_games()
    for game in games:
        start_scheduler(game, test_mode=False)

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()

@app.get("/files/login")
async def login(request: Request):
    redirect_uri = ""
    if ENVIRONMENT == "dev":
        print("redirect_uri for auth", redirect_uri)
        redirect_uri = request.url_for('auth_callback')
    else:
        redirect_uri = "https://aigames-dashboard-be-437522952831.asia-south1.run.app/auth/callback"
    print(f"🔗 Redirecting to Google OAuth with redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        print("⚠️ /auth/callback route HIT")
        token = await oauth.google.authorize_access_token(request)
        print("✅ Token received:", token)
        user_info = token.get("userinfo")
        print("🔍 User info:", user_info)
        email = user_info["email"]
        print(email)
        domain = email.split("@")[-1]
        print(f"🔍 User email domain: {domain}")
        existing_user = userService.get_user_by_email(email)
        print("🔍 Existing user:", existing_user)
        if not existing_user:
            user_data = UserModel(username=user_info["name"], email=email)
            created_user = userService.create_user(user_data)
            user_id = created_user.userId
            print("🆕 User created in Firestore:", created_user)
        else:
            print("✅ User already exists:", existing_user)
            user_id = existing_user.userId
        access_token = token["access_token"]
        print(f"✅ Google login successful: {user_info}")
        base_url = "http://localhost:8080/" if ENVIRONMENT == "dev" else "https://terra-ai-games-dash.vercel.app/"
        redirect_url = (
            f"{base_url}login-success"
            f"?token={access_token}"
            f"&email={user_info['email']}"
            f"&name={user_info['name']}"
            f"&userId={user_id}"
        )
        return RedirectResponse(redirect_url)
    except RequestException  as e:
        print(f"❌ Google OAuth failed: {e}")
        base_error_url = "http://localhost:8080/" if ENVIRONMENT == "dev" else"https://terra-ai-games-dash.vercel.app/"
        return RedirectResponse(f"{base_error_url}unauthorized?error=oauth_failed")

@app.get("/files", response_model=List[str])
def list_files(game_id: str = ""):
    files = googleStorageService.list_files(game_id)
    print("game_id from lis files", game_id)
    return files

@app.get("/files/content")
def get_file_content(path: str):
    print("path for test", path)
    content = googleStorageService.read_file(path)
    return {"filename": path, "content": content}

@app.post("/files/upload")
async def upload_file(path: str = Form(...), file: UploadFile = File(...), username: str = Form(...)):
    try:
        content = await file.read()
        googleStorageService.upload_file(path, content, updated_by=username)
        return {"message": "File uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.put("/files/update")
def update_file(path: str, content: str = Body(..., embed=True), username: str = Body(..., embed=True)):
    googleStorageService.update_file(path, content, updated_by=username)
    return {"message": "File updated successfully"}

@app.delete("/files/delete")
def delete_file(path: str):
    try:
        googleStorageService.delete_file(path)
        return {"message": "File deleted successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/files/meta/{gameName}")
def list_meta(gameName: str):
    files = fileServices.list_files(gameName)
    # fileServices.delete_dups()
    print("meta data files", files)
    return files

@app.get("/files/logs/{fileId}")
def get_logs(fileId: str) -> List[Dict]:
    logs = logServices.list_logs(fileId)
    return logs

@app.get("/files/games")
def get_all_games():
    return googleStorageService.list_games()

@app.post("/files/game/create")
def create_game(game_id: str):
    return googleStorageService.create_game(game_id)

@app.delete("/files/game/delete")
def delete_game(game_id: str):
    return googleStorageService.delete_game(game_id)