from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

if os.environ.get("DJANGO_SETTINGS_MODULE") is None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.local")

app = Celery("jurin")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "hard_delete_users": {
        "task": "jurin.users.tasks.hard_delete_users_task",
        "schedule": crontab(minute="0", hour="0"),
    },
    "create_daily_price": {
        "task": "jurin.stocks.tasks.create_daily_price_task",
        "schedule": crontab(minute="55", hour="23"),
    },
}
