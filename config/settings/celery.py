from config.env import env


CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

CELERY_RESULT_BACKEND = "django-db"

CELERY_TIMEZONE = "Asia/Seoul"

CELERY_TASK_SOFT_TIME_LIMIT = 20  # seconds
CELERY_TASK_TIME_LIMIT = 30  # seconds
CELERY_TASK_MAX_RETRIES = 3
