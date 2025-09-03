from apscheduler.schedulers.background import BackgroundScheduler
from app.core.jobs.upload_to_gemini import upload_files_to_gemini

scheduler = BackgroundScheduler()

def start_scheduler(game_id: str, test_mode: bool = False):

    if test_mode:
        scheduler.add_job(
            lambda: upload_files_to_gemini(game_id),
            trigger="interval",
            seconds=30,
            id=f"gemini_upload_job_{game_id}",
            replace_existing=True,
        )
    else:
        scheduler.add_job(
            lambda: upload_files_to_gemini(game_id),
            trigger="cron",
            hour=1,
            minute=0,
            timezone="Asia/Kolkata",
            id=f"gemini_upload_job_{game_id}",
            replace_existing=True,
        )
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")

    print(f"Job scheduled for game={game_id}, test_mode={test_mode}")
    print(f"Scheduler started (test_mode={test_mode})")