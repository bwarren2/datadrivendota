from django.conf import settings


def feature_flag(request):
    new_vars = {}
    for flag in settings.FEATURE_FLAGS:
        new_vars[flag] = getattr(settings, flag)
    return new_vars
