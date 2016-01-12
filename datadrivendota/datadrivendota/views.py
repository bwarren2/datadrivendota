from json import dumps

from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView as DjangoFormView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation

from .forms import SearchForm
from heroes.models import Hero
from leagues.models import League
from blog.models import Entry


class LandingView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):

        kwargs['blog_entry'] = Entry.public.all().order_by(
            '-created'
        ).first()

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


class ComboboxAjaxView(AjaxView):

    def get_result_data(self, **kwargs):

        q = self.request.GET.get('q', '')
        heroes = Hero.objects.filter(name__icontains=q)[:5]

        alignments = ['Strength', 'Agility', 'Intelligence']
        matched_alignments = [s for s in alignments if q.lower() in s.lower()]

        results = []

        for hero in heroes:
            match_json = {}
            match_json['id'] = hero.steam_id
            match_json['label'] = hero.css_id  # Attr
            match_json['value'] = hero.name  # Goes visible

            results.append(match_json)

        for i, string in enumerate(matched_alignments):
            match_json = {}
            match_json['id'] = i
            match_json['label'] = string.lower()  # Attr
            match_json['value'] = string  # Goes visible
            results.append(match_json)

        kwargs['results'] = results
        return kwargs
