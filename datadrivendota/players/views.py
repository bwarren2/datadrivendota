"""Views primarily related to players, as a group or particularly."""
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters

from datadrivendota.mixins import SubscriberRequiredMixin
from django.db.models import When, Case, Value, IntegerField, Sum

from .serializers import PlayerWinrateSerializer
from matches.models import PlayerMatchSummary
from .models import Player
from .serializers import PlayerSerializer


class PlayerIndexView(ListView):

    """A list of all updated players, aka clients."""

    paginate_by = 30
    queryset = Player.objects.filter(updated=True)


class FollowedPlayerIndexView(SubscriberRequiredMixin, ListView):

    """If the user is logged in, show the people they follow."""

    paginate_by = 30

    def get_queryset(self):
        """ Get the list of players to display."""
        return self.request.user.userprofile.following.all()


class ProIndexView(ListView):

    """List the players that have pro names."""

    paginate_by = 30

    def get_queryset(self):
        """ Get the list of players to display."""
        return Player.objects.exclude(pro_name=None)


class PlayerDetailView(DetailView):

    """ Get a closer look at a particular player."""

    def get_object(self):
        return get_object_or_404(Player, steam_id=self.kwargs.get('player_id'))

    def get_context_data(self, **kwargs):
        """Add in win statistics and a comparison player."""
        kwargs['player'] = self.object
        kwargs['pms_list'] = self.object.summaries(36)
        # self.add_comparison(**kwargs)

        stats = {}
        stats['wins'] = self.object.wins
        stats['losses'] = self.object.losses
        stats['total'] = self.object.games
        stats['winrate'] = self.get_winrate(stats)
        kwargs['stats'] = stats

        # Compare to dendi and s4 by default
        player_list = [70388657, 41231571, self.object.steam_id]
        endgame_players = Player.objects.filter(steam_id__in=player_list)
        kwargs['player_ids'] = ",".join(
            [str(p.steam_id) for p in endgame_players]
        )
        return super(PlayerDetailView, self).get_context_data(**kwargs)

    def get_winrate(self, stats):
        """ Calculate a winrate, allowing for the option of no games played."""
        if stats['total'] > 0:
            return round(float(stats['wins']) / stats['total'] * 100)
        else:
            return 0


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF viewset for player objects."""

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('persona_name',)
    paginate_by = 10


class PlayerWinrateViewSet(viewsets.ReadOnlyModelViewSet):

    """
    DRF player winrate endpoint.

    Useful for seeing who is best with a hero.
    """

    paginate_by = None
    serializer_class = PlayerWinrateSerializer

    def get_queryset(self):

        data_queryset = PlayerMatchSummary.objects.given(self.request)
        print Player.pros.all()
        data_queryset = data_queryset.filter(player__in=Player.pros.all())
        print data_queryset

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
