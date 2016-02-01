from json import dumps

from django.utils.decorators import method_decorator
from django.http import HttpResponse, Http404
from django.views.generic import View, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages

from parserpipe.forms import MatchRequestForm

from parserpipe.models import MatchRequest
from parserpipe.management.tasks import (
    KickoffMatchRequests,
    ReadParseResults,
    UpdatePmsReplays,
    MergeMatchRequestReplay
)
from matches.management.tasks import MirrorMatches
from datadrivendota.views import LoginRequiredView
from accounts.exceptions import DataCapReached, ValidationException


class DashView(TemplateView):
    template_name = 'parserpipe/dash.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(DashView, self).dispatch(*args, **kwargs)


class TasksView(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.user.is_staff:

            response_data = {}
            print request.POST
            match_id = request.POST['match_id']
            filename = request.POST['filename']
            task = request.POST['task']

            if task == 'create':
                mr, created = MatchRequest.objects.get_or_create(
                    requester=request.user,
                    match_id=match_id,
                    status=MatchRequest.SUBMITTED
                )
                if created:
                    response_data['result'] = 'Match Request Created'
                    response_data['type'] = 'success'
                else:
                    response_data['result'] = 'Match Request Already Exists'
                    response_data['type'] = 'warning'

            elif task == 'kickoff_submitted':
                KickoffMatchRequests().delay()
                response_data['result'] = 'Kicked off Submitted'
                response_data['type'] = 'success'

            elif task == 'kickoff_all':
                KickoffMatchRequests().delay(only_use_submitted=False)
                response_data['result'] = 'Kicked off aggressively'
                response_data['type'] = 'success'

            elif task == 'read_java':
                ReadParseResults().delay()
                response_data['result'] = 'Reading results'
                response_data['type'] = 'success'

            elif task == 'merge_results':
                json_data = {
                    'match_id': match_id,
                    'filename': filename,
                }
                MergeMatchRequestReplay().delay(json_data)
                response_data['result'] = 'Merging results'
                response_data['type'] = 'success'

            elif task == 'fanout':
                MergeMatchRequestReplay().fan_parsing(match_id=match_id)
                response_data['result'] = 'Fanning out'
                response_data['type'] = 'success'

            elif task == 'parse':
                UpdatePmsReplays().delay(match_id=match_id)
                response_data['result'] = 'Reading results'
                response_data['type'] = 'success'

            return HttpResponse(
                dumps(response_data),
                content_type="application/json"
            )
        else:
            raise Http404


class MatchRequestView(LoginRequiredView, FormView):
    form_class = MatchRequestForm
    template_name = 'accounts/match_import_request.html'
    initial = {}

    def form_invalid(self, form):
        super(MatchRequestView, self).form_invalid(form)

    def form_valid(self, form):

        match_id = form.cleaned_data['match_id']
        try:
            match_request = MatchRequest.create_for_user(
                self.request.user, match_id
            )

            msg = (
                "Request submitted!  We have tossed this in the task queue.  "
                "It should be finished in the next two minutes, and then "
                "<a href='{0}'>this link</a> will work"
            ).format(
                reverse(
                    'matches:detail',
                    kwargs={'match_id': match_request.match_id}
                ))
            task = MirrorMatches()
            task.delay(matches=[match_request.match_id])
            messages.add_message(self.request, messages.SUCCESS, msg)

        except ValidationException as err:
            msg = err.strerror
            messages.add_message(self.request, messages.WARNING, msg)
        except DataCapReached:
            msg = ("You have reached your import cap.",
                   "  We are working at increasing this.")
            messages.add_message(self.request, messages.WARNING, msg)
        return render(
            self.request,
            self.template_name,
            {
                'form': form
            }
        )

    def get_success_url(self):
        return reverse('players:management')