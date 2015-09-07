from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404

from utils.views import cast_dict, ability_infodict

from .models import Match, PlayerMatchSummary, PickBan


class MatchDetail(DetailView):

    def get_object(self):
        return get_object_or_404(Match, steam_id=self.kwargs.get('match_id'))

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.object
        summaries = PlayerMatchSummary.objects.filter(
            match=self.object
        ).select_related().order_by('player_slot')

        for summary in summaries:
            summary.kda = summary.kills - summary.deaths + .5 * summary.assists

            if summary.side == 'Radiant':
                summary.is_radiant = True
            else:
                summary.is_dire = True

        kwargs['summaries'] = summaries

        radiant_summaries = [
            summary for summary in summaries if summary.side == 'Radiant'
        ]
        radiant_infodict = {}
        radiant_cast_list = []
        min_skill_length = 10
        for summary in radiant_summaries:
            radiant_cast_list.append(cast_dict(summary))
            radiant_infodict[summary.player_slot] = ability_infodict(summary)
            min_skill_length = min(
                min_skill_length,
                len(radiant_infodict[summary.player_slot]['ability_dict'])
            )
        kwargs['radiant_summaries'] = radiant_summaries
        kwargs['radiant_infodict'] = radiant_infodict
        kwargs['radiant_cast_list'] = radiant_cast_list

        dire_summaries = [
            summary for summary in summaries if summary.side == 'Dire'
        ]
        dire_infodict = {}
        dire_cast_list = []
        for summary in dire_summaries:
            dire_cast_list.append(cast_dict(summary))
            dire_infodict[summary.player_slot] = ability_infodict(summary)
            min_skill_length = min(
                min_skill_length,
                len(dire_infodict[summary.player_slot]['ability_dict'])
            )

        kwargs['dire_summaries'] = dire_summaries
        kwargs['dire_infodict'] = dire_infodict
        kwargs['dire_cast_list'] = dire_cast_list

        kwargs['min_skill_length'] = min_skill_length

        # Identify any pickbans for templating.
        try:
            # Magic numbers are bad, but 0 = radiant.  Fix later
            dire_picks = PickBan.objects.filter(
                match=self.object,
                team=1,
                is_pick=True
            ).select_related('hero')

            dire_bans = PickBan.objects.filter(
                match=self.object,
                team=1,
                is_pick=False
            ).select_related('hero')

            radiant_picks = PickBan.objects.filter(
                match=self.object,
                is_pick=True
            ).exclude(team=1).select_related('hero')

            radiant_bans = PickBan.objects.filter(
                match=self.object,
                is_pick=False
            ).exclude(team=1).select_related('hero')

            pickban_length = (
                dire_picks.count() +
                dire_bans.count() +
                radiant_picks.count() +
                radiant_bans.count()
            )

            kwargs['dire_picks'] = dire_picks
            kwargs['dire_bans'] = dire_bans
            kwargs['radiant_picks'] = radiant_picks
            kwargs['radiant_bans'] = radiant_bans
            kwargs['pickban_length'] = pickban_length

        except IndexError:
            raise
        finally:
            return super(MatchDetail, self).get_context_data(**kwargs)


class MatchReplayDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/replay_parse.html'


class MatchListView(ListView):
    model = Match
    queryset = Match.objects.filter(
        validity=Match.LEGIT,
    ).select_related()[:20]
