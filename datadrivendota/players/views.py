"""Views primarily related to players, as a group or particularly."""
from random import choice
from rest_framework import viewsets, filters

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView


from datadrivendota.mixins import SubscriberRequiredMixin

from .models import Player
from heroes.models import Hero
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

    model = Player
    slug_url_kwarg = 'player_id'
    slug_field = 'steam_id'

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

    # def add_comparison(self, **kwargs):
    #     """Merge in comparison data if it exists."""
    #     p2s = Player.objects.exclude(pro_name=None,)\
    #         .exclude(steam_id=self.object.steam_id,)

    #     try:
    #         p2 = choice([p for p in p2s])

    #         kwargs['compare_url'] = reverse(
    #             'players:comparison',
    #             kwargs={
    #                 'player_id_1': self.object.steam_id,
    #                 'player_id_2': p2.steam_id,
    #             })
    #         kwargs['compare_str'] = 'Compare {p1} to {p2}!'.format(
    #             p1=self.object.display_name,
    #             p2=p2.display_name,
    #         )
    #     except IndexError:
    #         # If there are no other players, like in tests,
    #         # this is not a breaking requirement.
    #         pass
    #     return kwargs


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF viewset for player objects."""

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('persona_name',)
    paginate_by = 10


class PlayerComparsionView(TemplateView):

    """ View for player-player comparsion."""

    template_name = 'players/comparison.html'

    def get_context_data(self, **kwargs):
        """ Merge in the requested players or 404. """
        kwargs['player_1'] = get_object_or_404(
            Player, steam_id=kwargs['player_id_1']
        )
        kwargs['player_2'] = get_object_or_404(
            Player, steam_id=kwargs['player_id_2']
        )


class HeroStyleView(TemplateView):

    """Chart set for contextualizing  a player's use of a hero."""

    template_name = 'players/hero_style.html'

    def get_context_data(self, **kwargs):
        """ Get the player and hero requested. """
        kwargs['player'] = get_object_or_404(
            Player, steam_id=kwargs['player_id']
        )
        kwargs['hero'] = get_object_or_404(
            Hero, machine_name=kwargs['hero_name']
        )
