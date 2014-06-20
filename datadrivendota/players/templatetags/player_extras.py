from django import template
from django.core.urlresolvers import reverse

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
        return "<a href='{}'>{}</a>".format(link, text)
    except:
        return text
