from rest_framework import viewsets, filters
from django.db.models import When, Case, Value, IntegerField, Sum

from .serializers import PlayerWinrateSerializer, PlayerSerializer

from .models import Player
from matches.models import PlayerMatchSummary


# class PlayerViewSet(viewsets.ReadOnlyModelViewSet):

#     """ DRF viewset for player objects."""

#     queryset = Player.objects.all()
#     serializer_class = PlayerSerializer
#     lookup_field = 'steam_id'
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('persona_name',)
#     paginate_by = 10
#     paginate_by_param = 'page_size'
#     max_paginate_by = 10


class PlayerWinrateViewSet(viewsets.ReadOnlyModelViewSet):

    """
    DRF player winrate endpoint.

    Useful for seeing who is best with a hero.
    """

    paginate_by = None
    serializer_class = PlayerWinrateSerializer

    def get_queryset(self):

        data_queryset = PlayerMatchSummary.objects.given(self.request)
        data_queryset = data_queryset.filter(player__in=Player.pros.all())

        data_queryset = data_queryset.values('player__steam_id')\
            .order_by()\
            .annotate(
                wins=Sum(
                    Case(
                        When(is_win=True, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                losses=Sum(
                    Case(
                        When(is_win=False, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                games=Sum(
                    Case(
                        default=Value(1),
                        output_field=IntegerField()
                    )
                )
        )

        return data_queryset
