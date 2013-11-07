from django.core.mail import send_mail

def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def error_email(subject, content):
    send_mail(subject,content,'datadrivendota@gmail.com',
        ['datadrivendota@gmail.com'],fail_silently=False)
