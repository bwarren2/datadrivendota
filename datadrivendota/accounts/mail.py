from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import get_template

from django.core.mail import send_mail

import logging
logger = logging.getLogger(__name__)


def send_validation(strategy, backend, code):
    url = '{0}?verification_code={1}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code
    )
    url = strategy.request.build_absolute_uri(url)

    context = RequestContext(
        strategy.request,
        {
            'verify_url': url,
        }
    )

    subject = get_template(
        'accounts/confirmation_subject.txt'
    ).render(context).strip()
    from_email = settings.EMAIL_FROM
    to = code.email
    text_content = get_template(
        'accounts/confirmation_body.txt'
    ).render(context)
    html_content = get_template(
        'accounts/confirmation_body.html'
    ).render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    logger.warning('New user email validation: {0}'.format(code.email))

    send_mail(
        'New user!',
        str(code.email),
        settings.EMAIL_FROM,
        ['ben@datadrivendota.com'],
        fail_silently=False
    )
