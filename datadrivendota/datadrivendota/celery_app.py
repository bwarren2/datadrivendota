from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datadrivendota.settings.production')
app = Celery('datadrivendota')


#app.config_from_object('celery_config')
app.config_from_object('django.conf:settings')

if __name__ == '__main__':
    app.start()

