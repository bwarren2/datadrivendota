import json
from rest_framework import viewsets, filters
from itertools import chain
from heroes.models import Role

from django.views.generic import DetailView, ListView

from datadrivendota.views import AjaxView
from utils.views import cast_dict, ability_infodict
from heroes.models import Hero
from .models import Match, PlayerMatchSummary, PickBan

from .serializers import MatchSerializer, PlayerMatchSummarySerializer


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    paginate_by = 10
    serializer_class = MatchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class PlayerMatchSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerMatchSummarySerializer
    paginate_by = 10

    def get_queryset(self):
        queryset = PlayerMatchSummary.objects.all()

        player = self.request.query_params.get('player_id')
        if player is not None:
            queryset.filter(player__steam_id=player)
        valid = self.request.query_params.get('validity')
        if valid is not None:
            if valid == 'LEGIT':
                queryset.filter(match__validity=Match.LEGIT)
            elif valid == 'ALL':
                pass
            else:
                pass
        return queryset


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


class ComboboxAjaxView(AjaxView):

    def get_result_data(self, **kwargs):
        q = self.request.GET.get('search', '')
        heroes = [h.name for h in Hero.objects.filter(name__icontains=q)[:5]]
        alignments = ['Strength', 'Agility', 'Intelligence']
        matched_alignments = [s for s in alignments if q.lower() in s.lower()]
        roles = [r.name for r in Role.objects.filter(name__icontains=q)[:5]]
        results = []
        for i, string in enumerate(chain(heroes, matched_alignments, roles)):
            match_json = {}
            match_json['id'] = i
            match_json['label'] = string
            match_json['value'] = string
            results.append(match_json)
        kwargs['results'] = results
        return kwargs
