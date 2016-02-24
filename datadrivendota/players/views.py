"""Views primarily related to players, as a group or particularly."""
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from accounts.models import get_relevant_player_ids
from .models import Player


class PlayerIndexView(ListView):

    """A list of active or paid users."""

    paginate_by = 30
    # Player.objects.all()
    queryset = Player.objects.filter(steam_id__in=get_relevant_player_ids())


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
