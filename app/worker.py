from app.core.celery_app import celery_app

@celery_app.task(name="app.worker.analyze_resume_task")
def analyze_resume_task(resume_id: str, file_path: str):
    # 在 Repo A 中，這個函式體可以是空的
    # 因為 .delay() 只會把 name 和 args 送到 Redis
    pass