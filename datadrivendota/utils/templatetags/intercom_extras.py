import hashlib
import hmac

from django import template
from django.conf import settings

register = template.Library()


def generate_intercom_user_hash(user_steam_id):
    return hmac.new(
        settings.INTERCOM_API_SECRET,
        user_steam_id,
        digestmod=hashlib.sha256
    ).hexdigest()


@register.simple_tag
def intercom_user_hash(user):
    try:
        steam_id = user.social_auth.all()[0].extra_data['steamid']
        return generate_intercom_user_hash(steam_id)
    except Exception:
        return ""
