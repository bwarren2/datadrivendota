from json import dumps

from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView as DjangoFormView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q

from datadrivendota.keen_app import keen_client

from .forms import SearchForm
from players.models import Player
from heroes.models import Hero
from items.models import Item
from teams.models import Team
from leagues.models import League
from blog.models import Entry


class LandingView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        # Log the laod with keen
        keen_client.add_event(
            "splashpage_render", {
                "hit": 1,
            }
        )
        kwargs['blog_entry'] = Entry.public.all().order_by(
            '-created'
        )[0] or None
        return super(LandingView, self).get_context_data(**kwargs)


class LoginRequiredView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)


class JsonApiView(TemplateView):

    def get(self, request, *args, **kwargs):
        if request.is_ajax() or True:
            kwargs = self.get_context_data(**kwargs)
            return self.succeed(self.fetch_json(*args, **kwargs))
        else:
            raise SuspiciousOperation
            return self.fail()

    def succeed(self, json_data):
        response_data = {}
        response_data['result'] = 'success'
        response_data['data'] = json_data
        return HttpResponse(
            dumps(response_data),
            content_type="application/json"
        )

    def fail(self):
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


class SearchView(DjangoFormView):
    form_class = SearchForm
    template_name = 'search.html'

    def form_valid(self, form):
        search_str = form.cleaned_data['search_string']

        context = {
            'heroes': Hero.public.filter(
                name__icontains=(search_str)
            )[:10],
            'players': Player.objects.filter(
                persona_name__icontains=(search_str)
            )[:10],
            'pros': Player.objects.filter(
                pro_name__icontains=(search_str)
            )[:10],
            'teams': Team.objects.filter(
                Q(name__icontains=(search_str)) |
                Q(tag__icontains=(search_str))
            )[:10],
            'items': Item.objects.filter(
                name__icontains=(search_str)
            )[:10],
            'leagues': League.objects.filter(
                name__icontains=(search_str)
            )[:10],
            'form': form
        }

        return render(self.request, self.template_name, context)


class AjaxView(TemplateView):

    def get(self, request, *args, **kwargs):
        if request.is_ajax() or True:
            context = self.get_result_data(**kwargs)
            return self.succeed(context)
        else:
            return self.fail()

    def fail(self):
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    def succeed(self, context):
        data = dumps(context)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
