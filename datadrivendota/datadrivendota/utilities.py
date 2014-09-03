from django.core.mail import send_mail


def error_email(subject, content):
    send_mail(
        subject,
        content,
        # These next two lines should be pulled from settings. --kit 2014-02-16
        'ben@datadrivendota.com',
        ['ben@datadrivendota.com'],
        fail_silently=False
    )


class NoDataFound(BaseException):
    pass
