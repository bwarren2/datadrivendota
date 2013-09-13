from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

def logout_page(request):
    """
    Log out the user.
    """
    logout(request)
    return HttpResponseRedirect('/')


def base(request):

    if request.user.is_anonymous() or \
    request.user.social_auth.filter(provider='steam').count() == 0:
        extra_dict = {}
    else:
        extra_dict = request.user.social_auth.filter(provider='steam')[0].extra_data
    return render_to_response('base.html', extra_dict,
                              context_instance=RequestContext(request))

def about(request):

    return render_to_response('about.html',{},
                              context_instance=RequestContext(request))
