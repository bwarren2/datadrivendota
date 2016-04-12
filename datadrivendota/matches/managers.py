from django.db import models
from django.conf import settings


class Unparsed(models.Manager):

    def get_queryset(self):
        return super(Unparsed, self).get_queryset().filter(
            parsed_with=settings.PARSER_VERSION
        )


class Parsed(models.Manager):

    def get_queryset(self):
        return super(Parsed, self).get_queryset().filter(
            parsed_with=settings.PARSER_VERSION
        )
