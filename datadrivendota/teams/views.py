from django.views.generic import ListView, DetailView
from utils.pagination import SmarterPaginator
from .models import Team
from matches.models import Match, PlayerMatchSummary
from matches.views import annotated_matches


class TeamList(ListView):
    """The index of imported leagues"""
    model = Team

    def get_queryset(self):
        qs = self.model.objects.all().select_related()
        return qs


class TeamDetail(DetailView):
    """Focusing on a particular team"""

    def get_object(self):
        return Team.objects.get(steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        match_list = Match.objects.get(
            radiant_team_id=self.object.steam_id,
            skill=4)
        match_list = match_list.select_related()\
            .distinct().order_by('-start_time')

        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=match_list,
            per_page=15,
            current_page=page
        )
        match_list = paginator.current_page

        pms_list = PlayerMatchSummary.\
            objects.filter(match__in=match_list)\
            .select_related().order_by('-match__start_time')[:500]
        match_data = annotated_matches(pms_list, follow_list)

        context = {
            'match_list': match_list,
            'match_data': match_data,
        }
        super(TeamDetail, self).get_context_data(**context)
