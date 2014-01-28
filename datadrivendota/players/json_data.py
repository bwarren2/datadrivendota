from uuid import uuid4
import datetime
from time import mktime
from django.core.files import File
from django.db.models import Count
import json
from matches.models import PlayerMatchSummary, GameMode, Match
from .models import Player
from datadrivendota.r import s3File, enforceTheme, FailFace
from heroes.models import safen
from django.conf import settings
from utils.exceptions import NoDataFound


def player_winrate_breakout(player_id, game_mode_list=None, min_date=datetime.date(2009,1,1), max_date=None):
    if max_date==None:
        max_date_utc = mktime(datetime.datetime.now().timetuple())
    else:
        max_date_utc = mktime(max_date.timetuple())
    min_dt_utc = mktime(min_date.timetuple())

    if min_dt_utc > max_date_utc:
        raise NoDataFound
    if game_mode_list is None:
        game_mode_list = [gm.steam_id for gm in GameMode.objects.filter(is_competitive=True)]


    try:
        player = Player.objects.get(steam_id=player_id)
    except Player.DoesNotExist:
        raise NoDataFound
    annotations = PlayerMatchSummary.objects.filter(player=player, match__validity=Match.LEGIT).values('hero__machine_name','is_win').annotate(Count('is_win'))
    annotations = annotations.filter(match__duration__gte=settings.MIN_MATCH_LENGTH)
    annotations = annotations.filter(match__start_time__gte=min_dt_utc)
    annotations = annotations.filter(match__start_time__lte=max_date_utc)
    annotations = annotations.filter(match__game_mode__steam_id__in=game_mode_list)

    if len(annotations)==0:
        raise NoDataFound

    heroes = list(set([row['hero__machine_name'] for row in annotations]))
    wins = {row['hero__machine_name']: row['is_win__count'] for row in annotations if row['is_win']==True}
    losses = {row['hero__machine_name']: row['is_win__count'] for row in annotations if row['is_win']==False}

    win_rates = [float(wins.get(hero,0))/(wins.get(hero,0)+losses.get(hero,0))*100 for hero in heroes]
    games = [wins.get(hero,0)+losses.get(hero,0) for hero in heroes]
    labels = [safen(hero) for hero in heroes]

    return_json = json.dumps({
        'x_var': games,
        'y_var': win_rates,
        'labels': labels,
        })
    return return_json


    """  panel.lines(x=seq(0,100,1),y=100*(.5+(1/(2*sqrt(seq(0,100,1))))),lty=3,col='darkgray')
                  panel.lines(x=seq(0,100,1),y=100*(.5-(1/(2*sqrt(seq(0,100,1))))),lty=3,col='darkgray')
                  panel.lines(x=seq(0,100,1),y=100*(.5+2*(1/(2*sqrt(seq(0,100,1))))),lty=3,col='red')
                  panel.lines(x=seq(0,100,1),y=100*(.5-2*(1/(2*sqrt(seq(0,100,1))))),lty=3,col='red')
            """
