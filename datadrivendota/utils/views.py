from matches.models import SkillBuild


def cast_dict(summary):
    try:
        datadict = {
            'hero_mugshot': summary.hero.mugshot,
            'hero_mugshot_url': summary.hero.mugshot.url,
            'hero_name': summary.hero.name,
            'is_win': summary.is_win,
            'is_radiant': summary.which_side() == 'Radiant',
        }
    except ValueError:
        datadict = {
            'hero_mugshot': '',
            'hero_mugshot_url': '',
            'hero_name': summary.hero.name,
            'is_win': summary.is_win,
            'is_radiant': summary.which_side() == 'Radiant',
        }
    if summary.player.avatar is not None:
        datadict.update({'player_image': summary.player.avatar})
        if summary.player.persona_name is not None:
            datadict.update({'player_name': summary.player.display_name})
    return datadict


def ability_infodict(summary):
    try:
        datadict = {
            'hero_thumbshot': summary.hero.thumbshot,
            'hero_thumbshot_url': summary.hero.thumbshot.url,
            'hero_name': summary.hero.name,
            'hero_machine_name': summary.hero.machine_name,
            'ability_dict': [
                {
                    'name': sb.ability.name,
                    'machine_name': sb.ability.machine_name,
                    'picture_url': sb.ability.picture.url
                } for sb in SkillBuild.objects.filter(
                    player_match_summary=summary
                ).select_related()
            ]
        }
    except ValueError:
        datadict = {
            'hero_thumbshot': '',
            'hero_thumbshot_url': '',
            'hero_name': summary.hero.name,
            'hero_machine_name': summary.hero.machine_name,
            'ability_dict': [
                {
                    'machine_name': sb.ability.machine_name,
                    'picture_url': sb.ability.picture.url
                } for sb in SkillBuild.objects.filter(
                    player_match_summary=summary
                ).select_related()
            ]
        }
    return datadict
