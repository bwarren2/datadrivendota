from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery_app import app as celery_app  # nolint
# from django.apps import AppConfig


# class MyAppConfig(AppConfig):
#     def ready(self):
#         celery_app.tasks.refresh.delay()
