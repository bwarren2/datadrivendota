import json

from itertools import chain
from django.conf import settings
from heroes.models import HeroDossier, Hero, invalid_option
from matches.models import PlayerMatchSummary,  Match, fetch_match_attributes
from utils.exceptions import NoDataFound


def hero_vitals_json(hero_list, stats_list):
    # Currently, we are violating DRY with the available field listing from the form
    # and the R space being in different places and requiring that they are the same.

    selected_hero_dossiers = HeroDossier.objects.filter(hero__steam_id__in=hero_list)

    if len(selected_hero_dossiers) == 0 or invalid_option(stats_list):
        raise NoDataFound
    # Convention: Raw numbers that need to be modified to be right (like base
    # hero hp, which is always 150 at last check but gets gains from str, are
    # dubbed "base_".  A number inclusive of gains from stat growth is prefixless.
    # Modifiers (from stat points or items, w/e) will go into a "modified_"
    # variable, and final values (for plotting) are "final_")
    # NOTE: this convention is wrong with the numbers being imported as level 1
    # right now.
    return_pool={'level':[],'value':[],'hero':[],'stat':[]}
    for hero_dossier in selected_hero_dossiers:
        for stat in stats_list:
            for level in range(1,26):
                return_pool['level'].append(level)
                return_pool['value'].append(hero_dossier.level_stat(stat,level))
                return_pool['hero'].append(hero_dossier.hero.name)
                return_pool['stat'].append(stat)
    return json.dumps(return_pool)

def hero_lineup_json(heroes, stat, level):
    #Database pulls and format python objects to go to R
    hero_dossiers = HeroDossier.objects.all().select_related()
    selected_names = [h.name for h in Hero.objects.filter(steam_id__in=heroes)]
    if len(hero_dossiers)==0:
        raise NoDataFound

    try:
        hero_value = dict((dossier.hero.safe_name(), dossier.fetch_value(stat, level)) for dossier in hero_dossiers)
    except AttributeError:
        raise NoDataFound

    x_vals = [key for key in sorted(hero_value, key=hero_value.get, reverse=True)]
    y_vals = [hero_value[key] for key in sorted(hero_value, key=hero_value.get, reverse=True)]
    col_vec = [1 if name in selected_names else 0 for name in x_vals ]
    glom = {'HeroName':x_vals, 'Value':y_vals, 'Color':col_vec }
    return json.dumps(glom)

def hero_performance_json(hero, player, game_mode_list, x_var, y_var, group_var, split_var):


    #Database pulls and format python objects to go to R
    matches = PlayerMatchSummary.objects.filter(match__game_mode__in=game_mode_list)
    matches = matches.filter(match__duration__gte=settings.MIN_MATCH_LENGTH) #Ignore <10 min games
    matches = matches.filter(hero__steam_id=hero, match__validity=Match.LEGIT)
    skill1 = matches.filter(match__skill=1).select_related()[:100]
    skill2 = matches.filter(match__skill=2).select_related()[:100]
    skill3 = matches.filter(match__skill=3).select_related()[:100]
    for game in chain(skill1, skill2, skill3): game.skill_level=game.match.skill

    if player is not None:
        player_games = matches.filter(player__steam_id=player).select_related()
        for game in player_games: game.skill_level='Player'
        match_pool = list(chain(skill1, skill2, skill3, player_games))
    else:
        match_pool = list(chain(skill1, skill2, skill3))

    if len(match_pool)==0:
        raise NoDataFound

    try:
        x_vector_list, xlab = fetch_match_attributes(match_pool, x_var)
        y_vector_list, ylab = fetch_match_attributes(match_pool, y_var)
        match_list = fetch_match_attributes(match_pool, 'match_id')[0]
        if split_var is None:
            split_vector_list = ['No Split']
            split_lab = 'No Split'
        else:
            split_vector_list, split_lab = fetch_match_attributes(match_pool, split_var)
        if group_var is None:
            group_vector_list = ['No Grouping'] * len(x_vector_list)
            grouplab = 'No Grouping'
        else:
            group_vector_list, grouplab = fetch_match_attributes(match_pool, group_var)
    except AttributeError:
        raise NoDataFound

    return_json = json.dumps({
        'x_var': x_vector_list,
        'y_var': y_vector_list,
        'group_var': group_vector_list,
        'split_var': split_vector_list,
        'match_id': match_list,
        })
    return return_json, xlab, ylab, grouplab, split_lab
