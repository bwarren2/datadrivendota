from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.conf import settings


class UserCheckMixin(object):
    user_check_failure_path = ''  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return True

    def user_check_failed(self, request, *args, **kwargs):
        return redirect(self.user_check_failure_path)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_user(request.user):
            return self.user_check_failed(request, *args, **kwargs)
        return super(UserCheckMixin, self).dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin(UserCheckMixin):
    user_check_failure_path = 'login'  # can be path, url name or reverse_lazy

    def check_user(self, user):
        return user.is_superuser


class HealthIndexView(SuperuserRequiredMixin, TemplateView):
    template_name = 'health_index.html'

    def get_context_data(self, **kwargs):
        kwargs['read_key'] = settings.KEEN_READ_KEY
        kwargs['project_id'] = settings.KEEN_PROJECT_ID
        return super(HealthIndexView, self).get_context_data(**kwargs)
