from json import dumps
from os.path import basename

from django.shortcuts import render
from django.views.generic import View

from utils.file_management import outsourceJson
from utils.exceptions import NoDataFound

from datadrivendota.forms import KeyForm
from players.models import PermissionCode


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


class FormView(View):

    tour = None
    form = None
    attrs = None
    json_function = None
    title = None
    html = None

    def get(self, request):
        self.json_tour = dumps(self.tour)
        if request.GET:
            bound_form = self.form(request.GET)

            if bound_form.is_valid():
                try:
                    kwargs = {
                        attr: bound_form.cleaned_data[attr]
                        for attr in self.attrs
                    }
                    datalist, params = self.json_function(
                        **kwargs
                    )
                    params = self.amend_params(params)
                    json_data = outsourceJson(datalist, params)

                except NoDataFound:
                    return render(
                        request,
                        self.html,
                        {
                            'form': bound_form,
                            'error': 'error',
                            'title': self.title,
                            'tour': self.json_tour,
                        }
                    )

                return render(
                    request,
                    self.html,
                    {
                        'form': bound_form,
                        'json_data': basename(json_data.name),
                        'title': self.title,
                        'tour': self.json_tour,
                    }
                )
        else:
            form = self.form
            return render(
                request,
                self.html,
                {
                    'form': form,
                    'title': self.title,
                    'tour': self.json_tour,
                }
            )

    def amend_params(self, params):
        return params
