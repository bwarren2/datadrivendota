def active(request):
    return {
        'active': request.resolver_match.url_name
    }
