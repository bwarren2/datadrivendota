from django import template
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def player_link(player):
    if player is None:
        return ''
    if player.is_masked():
        return "Anonymous"

    if player.persona_name:
        text = player.display_name
    else:
        text = str(player.steam_id)

    try:
        link = reverse(
            'players:id_detail',
            kwargs={'player_id': player.steam_id}
        )
        return mark_safe("<a href='{}'>{}</a>".format(link, escape(text)))
    except:
        return text

player_link.is_safe = True
