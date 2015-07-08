
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import logout as auth_logout

from .serializers import MatchRequestSerializer
from rest_framework import viewsets
from social.backends.utils import load_backends
from accounts.models import MatchRequest
from datadrivendota.forms import MatchRequestForm
from matches.management.tasks import MirrorMatches

from datadrivendota.views import LoginRequiredView
from utils.exceptions import DataCapReached, ValidationException


class MatchRequestView(LoginRequiredView, FormView):
    form_class = MatchRequestForm
    template_name = 'accounts/match_import_request.html'
    initial = {}

    def form_invalid(self, form):
        super(MatchRequestView, self).form_invalid(form)

    def form_valid(self, form):

        match_id = form.cleaned_data['match_id']
        try:
            match_request = MatchRequest.create_for_user(
                self.request.user, match_id
            )

            msg = "Request submitted!  We have tossed this in the task queue.  It should be finished in the next two minutes, and then <a href='{0}'>this link</a> will work".format(
                reverse(
                    'matches:match_detail',
                    kwargs={'match_id': match_request.match_id}
                ))
            task = MirrorMatches()
            task.delay(matches=[match_request.match_id])
            messages.add_message(self.request, messages.SUCCESS, msg)

        except ValidationException as err:
            msg = err.strerror
            messages.add_message(self.request, messages.WARNING, msg)
        except DataCapReached:
            msg = ("You have reached your import cap.",
                   "  We are working at increasing this.")
            messages.add_message(self.request, messages.WARNING, msg)
        return render(
            self.request,
            self.template_name,
            {
                'form': form
            }
        )

    def get_success_url(self):
        return reverse('players:management')


class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        return kwargs


class LogoutView(TemplateView):
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(self, request, *args, **kwargs)


class CompleteView(TemplateView):
    template_name = 'accounts/home.html'

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        return kwargs


class AccountsHome(TemplateView):
    template_name = 'accounts/home.html'


class ValidationView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['validation_sent'] = True,
        kwargs['email'] = self.request.session.get('email_validation_address')
        kwargs = add_backends(kwargs)
        return kwargs


class EmailRequiredView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        backend = self.request.session['partial_pipeline']['backend']
        kwargs['email_required'] = True
        kwargs['backend'] = backend
        return kwargs


def add_backends(context):
    context['available_backends'] = load_backends(
        settings.AUTHENTICATION_BACKENDS
    )
    return context


class MatchRequestViewSet(viewsets.ModelViewSet):
    queryset = MatchRequest.objects.all()
    paginate_by = 10
    serializer_class = MatchRequestSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(requester=user)
