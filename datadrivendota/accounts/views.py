from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.auth import logout as auth_logout

from social.backends.utils import load_backends


@method_decorator(never_cache, name='dispatch')
class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        kwargs['method'] = self.kwargs.get('method', None)
        return kwargs


@method_decorator(never_cache, name='dispatch')
class LogoutView(TemplateView):
    template_name = 'accounts/logout.html'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(LogoutView, self).get(self, request, *args, **kwargs)


@method_decorator(never_cache, name='dispatch')
class CompleteView(TemplateView):
    template_name = 'accounts/home.html'

    def get_context_data(self, **kwargs):
        kwargs['available_backends'] = load_backends(
            settings.AUTHENTICATION_BACKENDS
        )
        return kwargs


@method_decorator(never_cache, name='dispatch')
class AccountsHome(TemplateView):
    template_name = 'accounts/home.html'


@method_decorator(never_cache, name='dispatch')
class ValidationView(TemplateView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        kwargs['validation_sent'] = True,
        kwargs['email'] = self.request.session.get('email_validation_address')
        kwargs = add_backends(kwargs)
        return kwargs


@method_decorator(never_cache, name='dispatch')
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
