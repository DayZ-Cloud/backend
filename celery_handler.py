import os

import dotenv
from celery import Celery

dotenv.load_dotenv()
redis = f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
celery_app = Celery(backend=redis, broker=redis)


@celery_app.task
def deploy_worker(text: str) -> str:
    return text