def active(request):
    try:
        ac = request.resolver_match.url_name
        return {
            'active': ac
        }
    except AttributeError:
        return {}

