from app.tasks.celery_app import celery_app
from app.tasks import drum_tasks

if __name__ == "__main__":
    celery_app.start()
