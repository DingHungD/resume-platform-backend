from celery import Celery
from app.core.config import settings

# 建立 Celery 實例
celery_app = Celery(
    "worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

# 基本配置
celery_app.conf.task_routes = {
    "app.worker.analyze_resume_task": "resume-queue"
}
celery_app.conf.update(task_track_started=True)