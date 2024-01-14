from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.django.local")

app = Celery("dump_in")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# app.conf.beat_schedule = {
#     "hard_delete_users": {
#         "task": "dump_in.users.tasks.hard_delete_users_task",
#         "schedule": crontab(minute="0", hour="0"),
#     },
# }
