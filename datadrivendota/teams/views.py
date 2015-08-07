import datetime

from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters

from utils.pagination import SmarterPaginator

from .serializers import TeamSerializer
from .models import Team
from matches.models import Match


class TeamList(ListView):

    """ The index of imported leagues. """

    model = Team
    paginate_by = 30
    template_name = 'teams/team_list.html'

    def get_queryset(self):
        qs = self.model.sorted.all()
        return qs

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=queryset,
            per_page=page_size,
            current_page=page
        )
        objs = paginator.current_page
        return (paginator, page, objs, True)


class TeamDetail(DetailView):

    """ Focusing on a particular team. """

    def get_object(self):
        return get_object_or_404(Team, steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        match_list = Match.objects.filter(
            skill=4
        )
        match_list = match_list.filter(
            Q(radiant_team__steam_id=self.object.steam_id) |
            Q(dire_team__steam_id=self.object.steam_id)
        )

        match_list = match_list.select_related()\
            .distinct().order_by('-start_time')

        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=match_list,
            per_page=15,
            current_page=page
        )
        match_list = paginator.current_page

        min_date = datetime.date.today() - datetime.timedelta(days=90)

        context = {
            'match_list': match_list,
            'min_date': min_date.isoformat(),
        }
        return super(TeamDetail, self).get_context_data(**context)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):

    """ List and detail for teams. """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    paginate_by = 10
