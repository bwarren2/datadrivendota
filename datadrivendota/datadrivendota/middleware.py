from django.conf import settings
from django.http import HttpResponseRedirect


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
