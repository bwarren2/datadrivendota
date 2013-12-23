from django.core.mail import send_mail
from uuid import uuid4
def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def error_email(subject, content):
    send_mail(subject,content,'datadrivendota@gmail.com',
        ['datadrivendota@gmail.com'],fail_silently=False)


###Auth Pipeline Stuff
def pipeline_test(backend, details, response, social_user, uid, user, *args, **kwargs):
    print backend, details, response, social_user, uid, user, args, kwargs
    return None

