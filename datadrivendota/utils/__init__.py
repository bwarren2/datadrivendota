from django.core.mail import send_mail
from math import factorial


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
    return '/matches/'+str(match_id)

def binomial_likelihood(n, k, p):
    choosing = factorial(n)/(factorial(k)*factorial(n-k))
    branching = p**k*(1-p)**(n-k)
    return choosing*branching


def binomial_exceedence(n, k, p):
    if n > 40:
        raise Exception("This code is not optimized for that!")
    odds = sum(binomial_likelihood(n, i, p) for i in range(k+1))

    return 1-odds
