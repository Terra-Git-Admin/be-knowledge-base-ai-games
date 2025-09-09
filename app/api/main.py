import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.storage import googleStorageService
from starlette.middleware.sessions import SessionMiddleware
from app.core.scheduler.geminiSchedular import start_scheduler, scheduler
from app.api.routes.files import fileRouter
from app.api.routes.filesMeta import filesMetaRouter
from app.api.routes.logs import logsRouter
from app.api.routes.games import gameRouter
from app.api.routes.auth import authRouter
from app.api.routes.deleteQueue import deleteQueueRouter
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=os.environ["SESSION_SECRET_KEY"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENVIRONMENT = os.environ["ENVIRONMENT"]

@app.get("/")
def root():
    return {"message": "Hello from FastAPI 🚀"}

app.include_router(fileRouter)
app.include_router(filesMetaRouter)
app.include_router(logsRouter)
app.include_router(gameRouter)
app.include_router(authRouter)
app.include_router(deleteQueueRouter)


@app.on_event("startup")
def on_startup():
    games = googleStorageService.list_games()
    for game in games:
        # start_scheduler(game, test_mode=True)
        start_scheduler(game, test_mode=False)

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()