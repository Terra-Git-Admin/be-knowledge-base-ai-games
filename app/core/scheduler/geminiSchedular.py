from apscheduler.schedulers.background import BackgroundScheduler
from app.core.jobs.upload_to_gemini import upload_files_to_gemini
from app.core.storage import googleStorageService

scheduler = BackgroundScheduler()


def get_all_games_for_gemini():
    games = googleStorageService.list_games()
    for game_id in games:
        upload_files_to_gemini(game_id)

def start_scheduler( test_mode: bool = False):

    if test_mode:
        scheduler.add_job(
            get_all_games_for_gemini,
            trigger="interval",
            seconds=5 * 60,
            id=f"gemini_upload_job_successful",
            replace_existing=True,
            max_instances=1
        )
    else:
        scheduler.add_job(
            get_all_games_for_gemini,
            trigger="cron",
            hour=1,
            minute=0,
            timezone="Asia/Kolkata",
            id=f"gemini_upload_job_successful",
            replace_existing=True,
        )
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")

    print(f"Scheduler started (test_mode={test_mode})")