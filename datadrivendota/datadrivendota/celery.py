from __future__ import absolute_import
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datadrivendota.settings.production')
app = Celery('datadrivendota')


#app.config_from_object('celery_config')
app.config_from_object('django.conf:settings')

if __name__ == '__main__':
    app.start()

