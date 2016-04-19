from django.conf import settings

from .querysets import FilteredQuerySet


class Unparsed(FilteredQuerySet):

    def get_queryset(self):
        return super(Unparsed, self).get_queryset().exclude(
            parsed_with=settings.PARSER_VERSION
        )


class Parsed(FilteredQuerySet):

    def get_queryset(self):
        return super(Parsed, self).get_queryset().filter(
            parsed_with=settings.PARSER_VERSION
        )
