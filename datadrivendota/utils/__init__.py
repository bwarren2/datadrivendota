from smtplib import SMTP
from django.core.mail import send_mail
import StringIO
import gzip
from django.conf import settings


def safen(str):
    return str.replace('-', ' ').replace('_', ' ').title()


def error_email(subject, content):
    send_mail(
        subject, content, 'ben@datadrivendota.com',
        ['ben@datadrivendota.com'], fail_silently=False
    )


def list_to_choice_list(items):
    return [(item, item.replace("_", " ").title()) for item in items]


def db_arg_map(lst, fn):
    l = []
    map(l.extend, [fn(x) for x in lst])
    return l


def match_url(match_id):
    """Yes, I know.  This is a dumb hack because calling reverse() a million times starts taking up a meaningful fraction of the load time.  At least this way the hack is centralized, and this function can be gutted if needed."""
    return '/matches/' + str(match_id)


def send_error_email(body):
    smtp = SMTP()
    debuglevel = 0
    smtp.set_debuglevel(debuglevel)
    smtp.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)

    smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    message_text = "Error! Failed with context:\n{0}\n\nBye\n".format(body)
    from_addr = "celery@datadrivendota.com"
    to_addr = "ben@datadrivendota.com"
    subj = 'Error!'
    msg = "From: {0}\nTo: {1}\nSubject: {2}\n\n{3}".format(
        from_addr, to_addr, subj, message_text
    )

    smtp.sendmail(from_addr, to_addr, msg)
    smtp.quit()


def gzip_str(content):
    out = StringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(content)
    return out.getvalue()


def gunzip_str(content):
    return gzip.GzipFile(fileobj=StringIO.StringIO(content)).read()
