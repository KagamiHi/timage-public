import os

from celery import Celery
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

app.config_from_object("backend.celeryconfig")
app.autodiscover_tasks()


# @app.on_after_finalize.connect
# def setup_startup_task(sender, **kwargs):
#     from bot.tasks import prepare_recommendations_valuables

#     prepare_recommendations_valuables.delay()
