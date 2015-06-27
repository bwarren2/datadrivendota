from json import dumps
from os.path import basename

from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView as DjangoFormView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q

from utils.exceptions import NoDataFound
from datadrivendota.keen_app import keen_client

from .forms import SearchForm
from players.models import Player
from heroes.models import Hero
from items.models import Item
from teams.models import Team
from leagues.models import League


class LandingView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        # Log the laod with keen
        keen_client.add_event(
            "splashpage_render", {
                "hit": 1,
            }
        )
        return super(LandingView, self).get_context_data(**kwargs)


class LoginRequiredView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)


class ApiView(View):

    def get(self, request):
        if (request.is_ajax() and request.GET) or True:
            try:
                bound_form = self.form(request.GET)
                if bound_form.is_valid():
                    kwargs = {}
                    for attr in self.attrs:
                        try:
                            kwargs.update(
                                {attr: bound_form.cleaned_data[attr]}
                            )
                        except KeyError:
                            pass
                    chart = self.json_function(
                        **kwargs
                    )
                    self.amend_params(request, chart)

                    json_data = chart.as_JSON()
                    return self.succeed(json_data)

                else:
                    return self.fail()

            except NoDataFound:
                return self.fail('No data')
        else:
            raise SuspiciousOperation
            return self.fail()

    def amend_params(self, request, chart):
        doctor_vars = {
            'width': 'outerWidth',
            'height': 'outerHeight',
            'draw_legend': 'draw_legend',
            'x_ticks': 'x_ticks',
            'y_ticks': 'y_ticks',
        }
        for var, adjust in doctor_vars.iteritems():
            reqvar = request.GET.get(var, None)
            if reqvar is not None:
                setattr(chart.params, adjust, reqvar)

        flag_vars = [
            'no_legend',
            'padding_bottom',
            'padding_top',
            'padding_left',
            'padding_right',
            'margin_bottom',
            'margin_top',
            'margin_left',
            'margin_right',
        ]
        for var in flag_vars:
            reqvar = request.GET.get(var, None)
            if reqvar is not None:
                if var == 'no_legend':
                    chart.params.draw_legend = False
                if var == 'padding_bottom':
                    chart.params.padding['bottom'] = int(reqvar)
                if var == 'padding_top':
                    chart.params.padding['top'] = int(reqvar)
                if var == 'padding_left':
                    chart.params.padding['left'] = int(reqvar)
                if var == 'padding_right':
                    chart.params.padding['right'] = int(reqvar)
                if var == 'margin_bottom':
                    chart.params.margin['bottom'] = int(reqvar)
                if var == 'margin_top':
                    chart.params.margin['top'] = int(reqvar)
                if var == 'margin_left':
                    chart.params.margin['left'] = int(reqvar)
                if var == 'margin_right':
                    chart.params.margin['right'] = int(reqvar)

    def succeed(self, json_data):
        response_data = {}
        response_data['result'] = 'success'
        response_data['url'] = settings.MEDIA_URL\
            + basename(json_data.name)
        return HttpResponse(
            dumps(response_data),
            content_type="application/json"
        )

    def fail(self, msg=None):
        data = 'fail: {0}'.format(msg)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


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
