from django import template

register = template.Library()


@register.simple_tag
def steam_id(user):
    try:
        return user.userprofile.player.steam_id
    except Exception:
        return ""


@register.simple_tag
def steam_avatar(user):
    try:
        return user.userprofile.player.avatar
    except Exception:
        return ""
