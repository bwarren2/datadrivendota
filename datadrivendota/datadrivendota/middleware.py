from django.http import HttpResponseRedirect
from social.apps.django_app.middleware import (
    SocialAuthExceptionMiddleware as BaseSocialAuthExceptionMiddleware,
)


class ForceHttps(object):
    def process_request(self, request):
        secure_request = (
            # settings.DEBUG,
            request.is_secure(),
            request.META.get("HTTP_X_FORWARDED_PROTO", "").lower() == "https",
        )
        if not any(secure_request):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace("http://", "https://")
            return HttpResponseRedirect(secure_url)


class SocialAuthExceptionMiddleware(BaseSocialAuthExceptionMiddleware):
    def get_message(self, request, exception):
        return (
            "Steam is having a bad day. "
            "Please try logging in again in a couple minutes."
        )

    def get_redirect_uri(self, request, exception):
        return "/"
