from django.db.models import When, Case, Value, IntegerField, Sum

from rest_framework import viewsets, filters
from rest_framework_extensions.cache.decorators import cache_response

from matches.models import PlayerMatchSummary, PickBan

from .serializers import (
    HeroSerializer,
    HeroDossierSerializer,
    HeroWinrateSerializer,
    HeroPickBanSerializer
)
from .models import Hero, HeroDossier


class HeroViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero endpoint. """

    queryset = Hero.objects.all()
    paginate_by = None
    serializer_class = HeroSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class HeroWinrateViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero winrate endpoint. """

    paginate_by = None
    serializer_class = HeroWinrateSerializer

    @cache_response()
    def retrieve(self, *args, **kwargs):
        return super(HeroWinrateViewSet, self).retrieve(*args, **kwargs)

    @cache_response()
    def list(self, *args, **kwargs):
        return super(HeroWinrateViewSet, self).list(*args, **kwargs)

    def get_queryset(self):

        data_queryset = PlayerMatchSummary.objects.given(self.request)

        data_queryset = data_queryset.values('hero__steam_id')\
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


class HeroPickBanViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero pickban endpoint. """

    paginate_by = None
    serializer_class = HeroPickBanSerializer

    @cache_response()
    def retrieve(self, *args, **kwargs):
        return super(HeroPickBanViewSet, self).retrieve(*args, **kwargs)

    @cache_response()
    def list(self, *args, **kwargs):
        return super(HeroPickBanViewSet, self).list(*args, **kwargs)

    def get_queryset(self):

        data_queryset = PickBan.objects.given(self.request)

        data_queryset = data_queryset.values('hero__steam_id')\
            .order_by()\
            .annotate(
                picks=Sum(
                    Case(
                        When(is_pick=True, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                bans=Sum(
                    Case(
                        When(is_pick=False, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                pick_or_bans=Sum(
                    Case(
                        default=Value(1),
                        output_field=IntegerField()
                    )
                )
        )
        return data_queryset


class HeroDossierViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero endpoint. """

    queryset = HeroDossier.objects.all()
    paginate_by = None
    serializer_class = HeroDossierSerializer

    @cache_response()
    def retrieve(self, *args, **kwargs):
        return super(HeroDossierViewSet, self).retrieve(*args, **kwargs)

    @cache_response()
    def list(self, *args, **kwargs):
        return super(HeroDossierViewSet, self).list(*args, **kwargs)
