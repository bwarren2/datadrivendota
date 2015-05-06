import logging
import importlib
from datetime import timedelta

from django.core.management.base import BaseCommand
from datadrivendota.celery_app import Config

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Call each task in the celerybeat schedule.
    """
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--faster-than',
            action='store',
            dest='faster_than',
            choices=['month', 'day', 'week', 'hour', 'minute']
        )

    def handle(self, *args, **options):
        print options['faster_than']

        if options['faster_than'] == 'month':
            testdelta = timedelta(weeks=4)
        elif options['faster_than'] == 'week':
            testdelta = timedelta(weeks=1)
        elif options['faster_than'] == 'day':
            testdelta = timedelta(days=1)
        elif options['faster_than'] == 'hour':
            testdelta = timedelta(hours=1)
        elif options['faster_than'] == 'minute':
            testdelta = timedelta(hours=1)

        for name, dct in Config.CELERYBEAT_SCHEDULE.items():
            if dct['schedule'] < testdelta:
                taskline = dct['task']

                path = ".".join(taskline.split('.')[:-1])
                taskname = taskline.split('.')[-1]

                module = importlib.import_module(path)
                task = getattr(module, taskname)
                print "Running: {0}".format(task)

                task().s().delay()
