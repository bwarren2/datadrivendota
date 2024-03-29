from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib import messages
from social.pipeline.partial import partial
from .models import UserProfile


@partial
def require_email(
    strategy, details, backend, user=None, is_new=False, *args, **kwargs
):
    if getattr(user, 'email', None) or backend.name != 'email':
        return

    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            messages.add_message(
                strategy.request,
                messages.WARNING,
                'Please use an email address :/'
            )
            return redirect('login')


@partial
def user_password(
    request, strategy, backend, user, is_new=False, *args, **kwargs
):
    if backend.name != 'email':
        return

    if is_new:
        password = kwargs['response']['password'][0]
        user.set_password(password)
        user.save()
    else:
        password = request['password']

        check = user.check_password(password)
        if not check:
            messages.add_message(
                strategy.request, messages.WARNING, 'Incorrect password :/'
            )
            return redirect('login')


def make_userprofile(
    request, strategy, backend, user, is_new=False, *args, **kwargs
):
    try:
        steam_id = int(
            kwargs.get('details', {}).get('player', {}).get('steamid', None)
        )
    except ValueError:
        steam_id = None
    UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'steam_id': steam_id,
        },
    )
    if is_new:
        send_mail(
            'New user!',
            str(user),
            settings.EMAIL_FROM,
            ['ben@datadrivendota.com'],
            fail_silently=False
        )
