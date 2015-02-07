from json import dumps
from os.path import basename
from functools import wraps

from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView as DjangoFormView
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q

from utils.file_management import outsourceJson, moveJson
from utils.exceptions import NoDataFound

from .forms import KeyForm, SearchForm
from players.models import Player
from accounts.models import PermissionCode
from heroes.models import Hero
from items.models import Item
from teams.models import Team
from leagues.models import League

try:
    if 'devserver' not in settings.INSTALLED_APPS:
        raise ImportError
    from devserver.modules.profile import devserver_profile
except ImportError:
    class devserver_profile(object):
        def __init__(self, *args, **kwargs):
            pass

        def __call__(self, func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return wraps(func)(nothing)


def base(request):
    p = Player.objects.get(steam_id=70388657)
    h = Hero.objects.get(name='Slark')
    # if (
    #     request.user.is_anonymous()
    #     or request.user.social_auth.filter(provider='steam').count() == 0
    # ):
    #     extra_dict = {
    #         'chart_player': p,
    #     }
    # else:
    #     extra_dict = request.user.social_auth.filter(
    #         provider='steam'
    #     )[0].extra_data
    #     extra_dict.update({'chart_player': p})
    extra_dict = {'chart_player': p, 'chart_hero': h}
    return render(request, 'home.html', extra_dict)


def blank(request):
    return render(request, 'base.html')


def faq(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')


def upgrade(request):
    if request.method == 'POST':
        form = KeyForm(request.POST)

        if request.user.is_authenticated():
            if form.is_valid():
                code = form.cleaned_data['code']
                try:
                    pcode = PermissionCode.objects.get(key=code)
                    application = pcode.associate(request.user.id)
                    if application:
                        msg = "Code applied successfully!  Privileges upgraded"
                    else:
                        if pcode.registrant is not None:
                            msg = "That code has been used already"
                        else:
                            msg = "Code failed to apply.  :("

                except PermissionCode.DoesNotExist:
                    msg = "We do not recognize that code."
            else:
                msg = ""
            return render(
                request,
                'registration/upgrade.html',
                {
                    'form': form,
                    'message': msg,
                }
            )
    else:
        form = KeyForm()
        return render(request, 'registration/upgrade.html', {'form': form})


class LoginRequiredView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredView, self).dispatch(*args, **kwargs)


class FormView(View):
    """This is an outdated method of dispatching and altering charts, scheduled for deprecation.  You can tell by the datalist, params entrypoint of times gone by, before class based charts.  ChartFormView is the preferred method now."""

    tour = None
    form = None
    attrs = None
    json_function = None
    title = None
    html = None

    def get(self, request):
        self.json_tour = dumps(self.tour)
        if request.GET:
            bound_form = self.form(request.GET)

            if bound_form.is_valid():
                try:
                    kwargs = {
                        attr: bound_form.cleaned_data[attr]
                        for attr in self.attrs
                    }

                    datalist, params = self.json_function(
                        **kwargs
                    )
                    params = self.amend_params(params)
                    json_data = outsourceJson(datalist, params)

                    return render(
                        request,
                        self.html,
                        {
                            'form': bound_form,
                            'json_data': basename(json_data.name),
                            'title': self.title,
                            'tour': self.json_tour,
                        }
                    )

                except NoDataFound:
                    return render(
                        request,
                        self.html,
                        {
                            'form': bound_form,
                            'error': 'error',
                            'title': self.title,
                            'tour': self.json_tour,
                        }
                    )

            else:
                return render(
                    request,
                    self.html,
                    {
                        'form': bound_form,
                        'title': self.title,
                        'tour': self.json_tour,
                    }
                )

        else:
            form = self.form
            return render(
                request,
                self.html,
                {
                    'form': form,
                    'title': self.title,
                    'tour': self.json_tour,
                }
            )

    def amend_params(self, params):
        return params


class ChartFormView(View):

    tour = None
    form = None
    attrs = None
    json_function = None
    title = None
    html = None

    def get(self, request):
        self.json_tour = dumps(self.tour)
        if request.GET:
            bound_form = self.form(request.GET)

            if bound_form.is_valid():
                try:
                    kwargs = {
                        attr: bound_form.cleaned_data[attr]
                        for attr in self.attrs
                    }

                    chart = self.json_function(
                        **kwargs
                    )
                    self.amend_params(chart)
                    json_data = moveJson(chart.as_JSON())
                    return render(
                        request,
                        self.html,
                        {
                            'form': bound_form,
                            'json_data': basename(json_data.name),
                            'title': self.title,
                            'tour': self.json_tour,
                        }
                    )

                except NoDataFound:
                    return render(
                        request,
                        self.html,
                        {
                            'form': bound_form,
                            'error': 'error',
                            'title': self.title,
                            'tour': self.json_tour,
                        }
                    )

            else:
                return render(
                    request,
                    self.html,
                    {
                        'form': bound_form,
                        'title': self.title,
                        'tour': self.json_tour,
                    }
                )

        else:
            form = self.form
            return render(
                request,
                self.html,
                {
                    'form': form,
                    'title': self.title,
                    'tour': self.json_tour,
                }
            )

    def amend_params(self, chart):
        return chart


class ApiView(View):

    def get(self, request):
        if (request.is_ajax() and request.GET):
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
                    json_data = moveJson(chart.as_JSON())

                    return self.succeed(json_data)

                else:
                    return self.fail()

            except NoDataFound:
                return self.fail()
        else:
            raise SuspiciousOperation
            return self.fail()

    def amend_params(self, request, chart):
        doctorVars = {
            'width': 'outerWidth',
            'height': 'outerHeight',
            'draw_legend': 'draw_legend',
            'x_ticks': 'x_ticks',
            'y_ticks': 'y_ticks',
        }
        for var, adjust in doctorVars.iteritems():
            reqvar = request.GET.get(var, None)
            if reqvar is not None:
                setattr(chart.params, adjust, reqvar)

        flagVars = [
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
        for var in flagVars:
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

    def fail(self):
        data = 'fail'
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
