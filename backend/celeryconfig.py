from celery.schedules import crontab
from django.conf import settings

broker_url = settings.CELERY_BROKER_URL
broker_connection_retry_on_startup = True

timezone = settings.TIME_ZONE
enable_utc = True

beat_scheduler = "common.utils.celery_scheduler:DatabaseSchedulerWithCleanup"
task_ignore_result = True

imports = [
    "bot.tasks",
]

beat_schedule = {
    "update-cluster-cache": {
        "task": "bot.tasks.prepare_recommendations_valuables",
        "schedule": crontab(minute="*/30"),
    },
    # "manage-tlg_subscriptions": {
    #     "task": "bot.tasks.manage_tlg_subscriptions",
    #     "schedule": crontab(minute="*/1"),
    # },
}
