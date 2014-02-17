from django.shortcuts import render
# from django.contrib.auth.decorators import permission_required
from datadrivendota.forms import KeyForm
from players.models import PermissionCode


# @permission_required('players.can_look')
def base(request):
    if (
            request.user.is_anonymous()
            or request.user.social_auth.filter(provider='steam').count() == 0
            ):
        extra_dict = {}
    else:
        extra_dict = request.user.social_auth.filter(
            provider='steam'
        )[0].extra_data
    return render(request, 'base.html', extra_dict)


def about(request):
    return render(request, 'about.html')


def privacy(request):
    return render(request, 'privacy.html')


def upgrade(request):
    if request.method == 'POST':
        form = KeyForm(request.POST)

        if request.user.is_authenticated():
            print request.user
            if form.is_valid():
                code = form.cleaned_data['code']
                try:
                    pcode = PermissionCode.objects.get(key=code)
                    application = pcode.associate(request.user.id)
                    if application:
                        msg = "Code applied successfully!  Privileges upgraded"
                    else:
                        if pcode.registrant is not None:
                            msg = "That code has been used already"
                        else:
                            msg = "Code failed to apply.  :("

                except PermissionCode.DoesNotExist:
                    msg = "We do not recognize that code."
            else:
                msg = ""
            return render(
                request,
                'registration/upgrade.html',
                {
                    'form': form,
                    'message': msg,
                }
            )
    else:
        form = KeyForm()
        return render(request, 'registration/upgrade.html', {'form': form})
