from django.core.mail import send_mail

def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def error_email(subject, content):
    send_mail(subject,content,'ben@datadrivendota.com',
        ['ben@datadrivendota.com'],fail_silently=False)

def list_to_choice_list(items):
    return [(item, item.replace("_", " ").title()) for item in items]
