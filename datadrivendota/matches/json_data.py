from itertools import chain
from matches.models import PlayerMatchSummary, Match, fetch_match_attributes,\
 fetch_single_attribute, fetch_attribute_label, SkillBuild
from utils.exceptions import NoDataFound
import json

def player_endgame_json(player_list,mode_list,x_var,y_var,split_var,group_var):


    selected_summaries = PlayerMatchSummary.objects.filter(
        player__steam_id__in=player_list,
        match__game_mode__steam_id__in=mode_list,
        match__validity=Match.LEGIT)
    selected_summaries = selected_summaries.select_related()
    if len(selected_summaries)==0:
        raise NoDataFound
    try:
        x_vector_list, xlab = fetch_match_attributes(selected_summaries, x_var)
        y_vector_list, ylab = fetch_match_attributes(selected_summaries, y_var)
        split_vector_list, split_lab = fetch_match_attributes(selected_summaries, split_var)
        group_vector_list, grouplab = fetch_match_attributes(selected_summaries, group_var)
        match_list = fetch_match_attributes(selected_summaries, 'match_id')[0]
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


def team_endgame_json(player_list,mode_list,x_var,y_var,split_var,group_var,compressor):

    radiant_matches = Match.objects.filter(game_mode__steam_id__in=mode_list, validity=Match.LEGIT)
    dire_matches = Match.objects.filter(game_mode__steam_id__in=mode_list, validity=Match.LEGIT)
    for player in player_list:
        radiant_matches = radiant_matches.filter(playermatchsummary__player__steam_id=player, playermatchsummary__player_slot__lte=5)
        dire_matches = dire_matches.filter(playermatchsummary__player__steam_id=player, playermatchsummary__player_slot__gte=5)

    if len(radiant_matches) + len(dire_matches)==0:
        raise NoDataFound
    radiant = PlayerMatchSummary.objects.filter(match__in=radiant_matches,player_slot__lte=5).select_related()
    dire = PlayerMatchSummary.objects.filter(match__in=dire_matches,player_slot__gte=5).select_related()

    pmses = list(chain(radiant,dire))
    x_data = dict([(p.match.steam_id,0) for p in pmses])
    y_data = dict([(p.match.steam_id,0) for p in pmses])
    group_data = dict([(p.match.steam_id, False) for p in pmses])
    split_data = dict([(p.match.steam_id, False) for p in pmses])

    for p in pmses:
        x_data[p.match.steam_id] += fetch_single_attribute(summary=p,
                                    attribute=x_var, compressor=compressor)
        y_data[p.match.steam_id] += fetch_single_attribute(summary=p,
                                    attribute=y_var, compressor=compressor)
        group_data[p.match.steam_id] = fetch_single_attribute(summary=p,
                                    attribute=group_var, compressor=compressor)
        split_data[p.match.steam_id] = fetch_single_attribute(summary=p,
                                    attribute=split_var, compressor=compressor)

    try:
        x_vector_list = [item for item in x_data.itervalues()]
        y_vector_list = [item for item in y_data.itervalues()]
        group_vector_list = [item for item in group_data.itervalues()]
        split_vector_list = [item for item in split_data.itervalues()]
        match_list = [key for key in split_data.iterkeys()]
        xlab = fetch_attribute_label(attribute=x_var)
        ylab = fetch_attribute_label(attribute=y_var) + " ({a})".format(a=compressor)
        grouplab = fetch_attribute_label(attribute=group_var)
    except AttributeError:
        raise NoDataFound

    return_json = json.dumps({
        'x_var': x_vector_list,
        'y_var': y_vector_list,
        'group_var': group_vector_list,
        'split_var': split_vector_list,
        'match_id': match_list,
        })
    return return_json, xlab, ylab, grouplab

def match_ability_json(match_id, split_var):
    skill_builds = SkillBuild.objects.filter(player_match_summary__match__steam_id=match_id).select_related().order_by('player_match_summary','level')

    x_list = []
    y_list = []
    group_list = []
    split_list = []
    for build in skill_builds:
        x_list.append(build.time/60.0)
        y_list.append(build.level)
        hero_name = build.player_match_summary.hero.name
        side = build.player_match_summary.which_side()
        group_list.append(hero_name)
        if split_var=='No Split':
            split_list.append('No Split')
        elif split_var=='hero':
            split_list.append("{hero} ({side})".format(hero=hero_name,side=side))
        elif split_var=='side':
            split_list.append(side)
        else:
            raise NoDataFound

    return_json = json.dumps({
        'x_var':x_list,
        'y_var':y_list,
        'group_var':group_list,
        'split_var': split_list,
        'x_lab': 'Time (m)',
        'y_lab': 'Level',
        'group_lab': 'Hero',
        'split_lab': 'Thingy'}
    )
    return return_json
