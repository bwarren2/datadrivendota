import json
from rest_framework import viewsets, filters

from django.views.generic import DetailView, ListView
from django.shortcuts import render
from django.views.generic.edit import FormView

from datadrivendota.views import ChartFormView, ApiView
from utils.views import cast_dict, ability_infodict
from heroes.models import Hero
from .models import Match, PlayerMatchSummary, PickBan
from .forms import ContextSelect
from .mixins import (
    EndgameMixin,
    OwnTeamEndgameMixin,
    SameTeamEndgameMixin,
    ProgressionListMixin,
    AbilityBuildMixin,
    MatchParameterMixin,
    SingleMatchParameterMixin,
    RoleMixin,
    SetProgressionMixin,
)
from .serializers import MatchSerializer, PlayerMatchSummarySerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    paginate_by = 10
    serializer_class = MatchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class PlayerMatchSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PlayerMatchSummary.objects.all()
    paginate_by = 10
    serializer_class = PlayerMatchSummarySerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class MatchDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.object
        summaries = PlayerMatchSummary.objects.filter(
            match=self.object
        ).select_related().order_by('player_slot')

        for summary in summaries:
            summary.kda = summary.kills - summary.deaths + .5*summary.assists

            if summary.side == 'Radiant':
                summary.is_radiant = True
            else:
                summary.is_dire = True

            if summary.leaver.steam_id != 0:
                summary.improper_player = True

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


class ParseMatchDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/parse_match.html'

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.object
        summaries = PlayerMatchSummary.objects.filter(
            match=self.object
        ).select_related().order_by('player_slot')

        slot_dict = {
            0: '#7CD51B',  # 1f77b4', #Radiant #7CD51B
            1: '#7CD51B',  # 7EF6C6',
            2: '#7CD51B',  # 9A1D9B',
            3: '#7CD51B',  # ECF14C',
            4: '#7CD51B',  # DB7226',
            128: '#BA3B15',  # E890BA',
            129: '#BA3B15',  # 99B15F',
            130: '#BA3B15',  # 75D1E1',
            131: '#BA3B15',  # 147335',
            132: '#BA3B15',  # 906A2B', #Dire  #BA3B15
        }
        kwargs['slot_dict'] = slot_dict

        css_color_dict = {}
        for summary in summaries:

            if summary.side == 'Radiant':
                summary.is_radiant = True
            else:
                summary.is_dire = True

            if summary.leaver.steam_id != 0:
                summary.improper_player = True

            css_color_dict[
                summary.hero.internal_name
            ] = slot_dict[summary.player_slot]
        kwargs['summaries'] = summaries

        radiant_summaries = [
            summary for summary in summaries if summary.side == 'Radiant'
        ]
        radiant_cast_list = []
        for summary in radiant_summaries:
            radiant_cast_list.append(cast_dict(summary))

        kwargs['radiant_cast_list'] = radiant_cast_list

        dire_summaries = [
            summary for summary in summaries if summary.side == 'Dire'
        ]
        dire_cast_list = []
        for summary in dire_summaries:
            dire_cast_list.append(cast_dict(summary))
        kwargs['dire_cast_list'] = dire_cast_list

        hero_id_names = {
            pms.hero.steam_id: pms.hero.internal_name
            for pms in summaries
        }
        kwargs['hero_id_names'] = json.dumps(hero_id_names)
        return super(ParseMatchDetail, self).get_context_data(**kwargs)


# Commenting out because we are gutting some functionality for the moment, but I don't want to delete so that the next refactoring step will be easier.  This should be gone within two weeks.  --ben 2015-04-19


class MatchListView(ListView):
    model = Match
    # results_per_page = 2
    # total_results = 5
    queryset = Match.objects.filter(
        validity=Match.LEGIT,
    ).select_related()[:20]

    # def paginate_queryset(self, queryset, page_size):
    #     print "Hai!"
    #     return None, None, None, None
    #     match_list = Match.objects.filter(
    #         validity=Match.LEGIT,
    #     )
    #     print len(self.match_list)
    #     match_list = match_list.select_related()\
    #         .distinct().order_by('-start_time')[:self.total_results]

    #     print len(self.match_list)
    #     page = self.request.GET.get('page')
    #     paginator = SmarterPaginator(
    #         object_list=match_list,
    #         per_page=self.results_per_page,
    #         current_page=page
    #     )
    #     self.match_list = paginator.current_page
    #     print len(self.match_list)
    #     pms_list = PlayerMatchSummary.\
    #         objects.filter(match__in=match_list)\
    #         .select_related().order_by('-match__start_time')[:500]
    #     self.match_data = annotated_matches(pms_list, [])

    #     return (paginator, page, page.object_list, page.has_other_pages())


# def follow_match_feed(request):
#     results_per_page = 20
#     total_results = 500

#     # One of the default load methods, without the form.
#     if request.method != 'POST':
#         form = FollowMatchForm()
#         try:
#             player = request_to_player(request)
#             follow_list = [
#                 follow for follow in player.userprofile.following.all()
#             ]
#             match_list = Match.objects.filter(
#                 validity=Match.LEGIT,
#                 playermatchsummary__player__in=follow_list
#             )
#             match_list = match_list.select_related()\
#                 .distinct().order_by('-start_time')[:total_results]

#             page = request.GET.get('page')
#             paginator = SmarterPaginator(
#                 object_list=match_list,
#                 per_page=results_per_page,
#                 current_page=page
#             )
#             match_list = paginator.current_page

#             pms_list = PlayerMatchSummary.\
#                 objects.filter(match__in=match_list)\
#                 .select_related().order_by('-match__start_time')[:500]
#             match_data = annotated_matches(pms_list, follow_list)
#             return render(
#                 request,
#                 'matches/follow.html',
#                 {
#                     'form': form,
#                     'match_list': match_list,
#                     'match_data': match_data,
#                 }
#             )

#         except AttributeError:
#             pro_list = Player.objects.exclude(pro_name=None)
#             match_list = Match.objects.filter(
#                 validity=Match.LEGIT,
#                 playermatchsummary__player__in=pro_list
#             )
#             match_list = match_list.select_related()\
#                 .distinct().order_by('-start_time')[:total_results]

#             page = request.GET.get('page')
#             paginator = SmarterPaginator(
#                 object_list=match_list,
#                 per_page=results_per_page,
#                 current_page=page
#             )
#             match_list = paginator.current_page

#             pms_list = PlayerMatchSummary.\
#                 objects.filter(match__in=match_list).select_related()

#             match_data = annotated_matches(pms_list, [])
#             return render(
#                 request,
#                 'matches/follow.html',
#                 {
#                     'form': form,
#                     'match_list': match_list,
#                     'match_data': match_data,
#                 }
#             )
#     #Using the form to submit
#     else:
#         form = FollowMatchForm(request.POST)
#         if form.is_valid():
#             match_list = Match.objects.filter(
#                 validity=Match.LEGIT,
#             )
#             if form.cleaned_data['hero'] is not None:
#                 match_list = match_list.filter(
#                     playermatchsummary__hero__steam_id=
#                     form.cleaned_data['hero'],
#                 )
#             if form.cleaned_data['player'] is not None:
#                 match_list = match_list.filter(
#                     playermatchsummary__player__steam_id=
#                     form.cleaned_data['player'],
#                 )
#             if form.cleaned_data['min_date'] is not None:
#                 min_date_utc = mktime(
#                     form.cleaned_data['min_date'].timetuple()
#                     )
#                 match_list = match_list.filter(
#                     start_time__gte=min_date_utc,
#                 )
#             if form.cleaned_data['max_date'] is not None:
#                 max_date_utc = mktime(
#                     form.cleaned_data['max_date'].timetuple()
#                     )
#                 match_list = match_list.filter(
#                     start_time__lte=max_date_utc,
#                 )

#             match_list = match_list.select_related()\
#                 .distinct().order_by('-start_time')[:total_results]

#             page = request.GET.get('page')
#             paginator = SmarterPaginator(
#                 object_list=match_list,
#                 per_page=results_per_page,
#                 current_page=page
#             )
#             match_list = paginator.current_page

#             pms_list = PlayerMatchSummary.\
#                 objects.filter(match__in=match_list).select_related()

#             match_data = annotated_matches(pms_list, [])
#             return render(
#                 request,
#                 'matches/follow.html',
#                 {
#                     'form': form,
#                     'match_list': match_list,
#                     'match_data': match_data,
#                 }
#             )
#         else:
#             return render(
#                 request,
#                 'matches/follow.html',
#                 {
#                     'form': form,
#                 }
#             )


class MatchHeroContext(FormView):
    template_name = 'matches/match_hero_context.html'
    form_class = ContextSelect

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)

        else:
            return self.form_invalid(form)
            return render(
                self.request,
                self.template_name,
                {'form': form_class()},
            )

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        if self.request.method in ('GET'):
            kwargs.update({
                'data': self.request.GET,
                'files': self.request.FILES,
            })

        return kwargs

    def form_valid(self, form):
        hero = form.cleaned_data['hero']

        hero_obj = Hero.objects.get(steam_id=hero)

        hero_name = hero_obj.name
        machine_name = hero_obj.machine_name
        matches = ",".join(str(x) for x in form.cleaned_data['matches'])
        outcome = form.cleaned_data['outcome']
        amendments = {
            'form': form,
            'hero': hero,
            'matches': matches,
            'outcome': outcome,
            'hero_name': hero_name,
            'machine_name': machine_name,
        }
        return render(
            self.request,
            self.template_name,
            self.get_context_data(**amendments),
            )


# Everything below here is deprecated and marked for near-term refactor.
# You are warned.

class MatchParameterChart(MatchParameterMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page scatterplots end-of-game data for a match of your choice."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare kills and hero damage to see who was killstealing in a match, or hero damage and gold to see who was producing a return on investment."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and match you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for teams, try other tabs.",
            'placement': "bottom"
        },
    ]
    title = "Match Parameter Scatter"
    html = "matches/form.html"


class Endgame(EndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for players of your choosing."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare kills-deaths+assists/2 (KDA2, kind of a net score) between imported players."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and players you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for teams, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: how do [A]kke's and Funn1k's KDA2s change based on win/loss?  Hint: tweak the group and split vars for different renderings."
        }
    ]
    title = "Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class OwnTeamEndgame(OwnTeamEndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for teams for each player of your choosing."
        }
    ]
    title = "Own-Team Endgame Charts"
    html = "matches/form.html"



class SameTeamEndgame(SameTeamEndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for groups of players."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare team kills to team assists for any game with the given players on the same team."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and players you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for individuals, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: When Funn1k, Dendi, and XBOCT play together, what KDA2 does their team exceed when they win?"
        }
    ]
    title = "Same Team Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class ProgressionList(ProgressionListMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts level progression data for specific players in specific matches."
        }
    ]
    title = "Match List Hero Progression"
    html = "matches/form.html"

    def amend_params(self, params):
        return params

class ProgressionSet(SetProgressionMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts level progression data for a specific hero in specific matches."
        }
    ]
    title = "Match Set Hero Progression"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class AbilityBuild(AbilityBuildMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page is one of the few to chart within-game data: it plots when people place skill points in a game, with the first point placement being 0 minutes."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can see how people leveled in game with Dendi on Magnus (550709502)."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which match id you want and output formatting here."
        },
        {
            'orphan': True,
            'title': "Important note!",
            'content': "This only works for games we have imported!  The data management page lets qualified users add players to the import process."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For the overview for a player, try players:index.  For the match overview, try /matches/<match-id>",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: in match 550709502, who slowed down when?  When did Slark and Lifesteal crush their enemies?"
        }
    ]
    title = "Match Ability Breakdown"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


# def combobox_tags(request):
#     if request.is_ajax():
#         q = request.GET.get('term', '')
#         heroes = [h.name for h in Hero.objects.filter(name__icontains=q)[:5]]
#         alignments = ['Strength', 'Agility', 'Intelligence']
#         matched_alignments = [s for s in alignments if q.lower() in s.lower()]
#         roles = [r.name for r in Role.objects.filter(name__icontains=q)[:5]]
#         results = []
#         for i, string in enumerate(chain(heroes, matched_alignments, roles)):
#             match_json = {}
#             match_json['id'] = i
#             match_json['label'] = string
#             match_json['value'] = string
#             results.append(match_json)
#         data = json.dumps(results)
#     else:
#         data = 'fail'
#     mimetype = 'application/json'
#     return HttpResponse(data, mimetype)


class ApiEndgameChart(EndgameMixin, ApiView):
    pass


class ApiOwnTeamEndgameChart(OwnTeamEndgameMixin, ApiView):
    pass


class ApiSameTeamEndgameChart(SameTeamEndgameMixin, ApiView):
    pass


class ApiProgressionListChart(ProgressionListMixin, ApiView):
    pass


class ApiAbilityBuildChart(AbilityBuildMixin, ApiView):
    pass


class ApiMatchScatterChart(MatchParameterMixin, ApiView):
    pass


class ApiMatchBarChart(SingleMatchParameterMixin, ApiView):
    pass


class ApiRoleChart(RoleMixin, ApiView):
    pass


class ApiSetProgressionChart(SetProgressionMixin, ApiView):
    pass
