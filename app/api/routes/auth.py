from fastapi import APIRouter, Request
import os
from app.auth.google_oauth import oauth
from fastapi.responses import RedirectResponse
from requests.exceptions import RequestException
from app.core.services.userService import userService
from app.core.schema.userSchema import UserModel




ENVIRONMENT = os.getenv("ENVIRONMENT", "prod")

authRouter = APIRouter(
    tags=["Auth"]
)

@authRouter.get("/files/login")
async def login(request: Request):
    redirect_uri = ""
    if ENVIRONMENT == "dev":
        print("redirect_uri for auth", redirect_uri)
        redirect_uri = request.url_for('auth_callback')
    else:
        redirect_uri = "https://aigames-dashboard-be-437522952831.asia-south1.run.app/auth/callback"
    print(f"🔗 Redirecting to Google OAuth with redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@authRouter.get("/auth/callback")
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

