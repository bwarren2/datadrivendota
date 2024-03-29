from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, FormView
from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import Http404
from django.contrib import messages

from social.apps.django_app.default.models import Code
from parserpipe.models import MatchRequest
from matches.models import Match, PlayerMatchSummary

from social.backends.utils import load_backends
from .forms import (
    ForgotPasswordForm,
    ResetPasswordForm,
    SteamIdForm
)


@method_decorator(never_cache, name='dispatch')
class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        kwargs['method'] = self.kwargs.get('method', None)
        return super(LoginView, self).get_context_data(**kwargs)


@method_decorator(never_cache, name='dispatch')
class LogoutView(TemplateView):
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(self, request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class ForgotPasswordFormView(FormView):
    template_name = 'accounts/forgot_password.html'
    form_class = ForgotPasswordForm
    success_url = reverse_lazy('accounts:forgot_pass_confirm')

    def form_valid(self, form):
        code = Code.make_code(self.request.POST['email'])
        send_reset_email(self.request, code)
        return super(ForgotPasswordFormView, self).form_valid(form)


@method_decorator(never_cache, name='dispatch')
class ForgotPassConfirmView(TemplateView):
    template_name = 'accounts/forgot_pass_confirm.html'


@method_decorator(never_cache, name='dispatch')
class ResetPasswordView(FormView):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        password = form.data['password']
        password_check = form.data['password_check']
        code = Code.get_code(self.kwargs['code'])
        if code is None:
            raise Http404('Missing token')

        if password == password_check:
            user = User.objects.get(email=code.email)
            user.set_password(password)
            user.save()
            code.verify()
            messages.add_message(
                self.request, messages.SUCCESS, 'Password updated!'
            )
            return super(ResetPasswordView, self).form_valid(form)

        else:
            messages.add_message(
                self.request, messages.WARNING, 'Passwords do not match.'
            )
            return super(ResetPasswordView, self).form_invalid(form)


@method_decorator(never_cache, name='dispatch')
class HomeView(FormView):
    form_class = SteamIdForm
    template_name = 'accounts/home.html'
    success_url = reverse_lazy('accounts:home')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        steam_id = int(form.data['steam_id'])
        userprofile = self.request.user.userprofile
        userprofile.steam_id = steam_id
        userprofile.save()

        messages.add_message(
            self.request, messages.SUCCESS, 'Steam ID Updated!'
        )
        return super(HomeView, self).form_valid(form)

    def get_context_data(self, **kwargs):

        requested_ids = MatchRequest.objects.filter(
            requester=self.request.user
        ).values_list('match_id', flat=True)

        kwargs['imported_matches'] = Match.parsed.filter(
            steam_id__in=requested_ids
        )

        imported_match_ids = Match.parsed.filter(
            steam_id__in=requested_ids
        ).values_list('steam_id', flat=True)

        kwargs['requested_matches'] = MatchRequest.objects.filter(
            requester=self.request.user,
        ).exclude(
            match_id__in=imported_match_ids
        )

        kwargs['recent_matches'] = PlayerMatchSummary.objects.filter(
            player__steam_id=self.request.user.userprofile.steam_id,
        )

        return super(HomeView, self).get_context_data(**kwargs)


@method_decorator(never_cache, name='dispatch')
class ValidationView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['validation_sent'] = True,
        kwargs['email'] = self.request.session.get('email_validation_address')
        kwargs = add_backends(kwargs)
        return super(ValidationView, self).get_context_data(**kwargs)


@method_decorator(never_cache, name='dispatch')
class EmailRequiredView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        backend = self.request.session['partial_pipeline']['backend']
        kwargs['email_required'] = True
        kwargs['backend'] = backend
        return super(EmailRequiredView, self).get_context_data(**kwargs)


@method_decorator(never_cache, name='dispatch')
class CompleteView(TemplateView):
    template_name = 'accounts/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CompleteView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        return super(CompleteView, self).get_context_data(**kwargs)


def add_backends(context):
    context['available_backends'] = load_backends(
        settings.AUTHENTICATION_BACKENDS
    )
    return context


def send_reset_email(request, code):

    url = reverse(
        'accounts:reset_password',
        kwargs={'code': code.code}
    )
    url = request.build_absolute_uri(url)
    send_mail(
        'Password Recovery',
        'Use this URL to reset your password {0}'.format(url),
        settings.EMAIL_FROM,
        [code.email],
        fail_silently=False
    )
