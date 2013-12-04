#from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

@permission_required('players.can_look')
def base(request):

    if request.user.is_anonymous() or \
    request.user.social_auth.filter(provider='steam').count() == 0:
        extra_dict = {}
    else:
        extra_dict = request.user.social_auth.filter(provider='steam')[0].extra_data
    return render(request, 'base.html', extra_dict)

def about(request):

    return render(request, 'about.html',{})
