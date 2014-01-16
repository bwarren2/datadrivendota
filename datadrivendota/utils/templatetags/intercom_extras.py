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
        steam_id = user.userprofile.player.steam_id
        return generate_intercom_user_hash(str(steam_id))
    except Exception:
        return ""
