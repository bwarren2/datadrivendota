from django.core.mail import send_mail
import StringIO
import gzip


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


def gzip_str(content):
    out = StringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(content)
    return out.getvalue()


def gunzip_str(content):
    return gzip.GzipFile(fileobj=StringIO.StringIO(content)).read()
