from django.shortcuts import redirect
from django.contrib import messages
from social.pipeline.partial import partial


@partial
def require_email(
    strategy, details, backend, user=None, is_new=False, *args, **kwargs
):
    if user.email or backend.name != 'email':
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
    password = strategy.request_data()['password']

    check = user.check_password(password)
    if is_new:
        user.set_password(password)
        user.save()
    elif not check:
        print check, user.password, password
        messages.add_message(
            strategy.request, messages.WARNING, 'Incorrect password :/'
        )
        return redirect('login')
