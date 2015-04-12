from django.core.mail import send_mail
from django.conf import settings


def error_email(subject, content):
    send_mail(
        subject,
        content,
        settings.ERROR_RECIPIENT_EMAIL,
        [settings.ERROR_RECIPIENT_EMAIL],
        fail_silently=False
    )


class NoDataFound(BaseException):
    pass
