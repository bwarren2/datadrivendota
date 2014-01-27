from django.core.management.base import BaseCommand

from django.template.loader import get_template
from django.template import Context


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('heroku_static_pages/error.html', 'w') as f:
            f.write(get_template('utils/error.html').render(Context({})))
        with open('heroku_static_pages/maintenance.html', 'w') as f:
            f.write(get_template('utils/maintenance.html').render(Context({})))
