from django.db import models


class Unparsed(models.Manager):

    def get_queryset(self):
        return super(Unparsed, self).get_queryset().filter(parsed_with=None)


class Parsed(models.Manager):

    def get_queryset(self):
        return super(Parsed, self).get_queryset().exclude(parsed_with=None)
