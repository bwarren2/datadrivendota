from django import template

register = template.Library()


@register.simple_tag
def steam_id(user):
    try:
        return user.social_auth.all()[0].extra_data['steamid']
    except Exception:
        return ""


@register.simple_tag
def steam_avatar(user):
    try:
        return user.social_auth.all()[0].extra_data['avatar']
    except Exception:
        return ""
