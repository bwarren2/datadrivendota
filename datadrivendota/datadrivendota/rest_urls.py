from rest_framework.routers import DefaultRouter
from matches.views import (
    MatchViewSet,
    PlayerMatchSummaryViewSet,
    SkillBuildViewSet
)
from teams.views import TeamViewSet
from leagues.views import LeagueViewSet
from heroes.views import (
    HeroViewSet,
    HeroDossierViewSet,
    HeroWinrateViewSet,
    HeroPickBanViewSet,
)
from items.views import ItemViewSet
from accounts.views import MatchRequestViewSet
from players.views import PlayerViewSet, PlayerWinrateViewSet


# DRF is great
router = DefaultRouter()
router.register('match-request', MatchRequestViewSet)
router.register('teams', TeamViewSet)
router.register('leagues', LeagueViewSet)
router.register('heroes', HeroViewSet)
router.register(
    'hero-winrate',
    HeroWinrateViewSet,
    base_name='hero-winrate'
)
router.register(
    'player-winrate',
    PlayerWinrateViewSet,
    base_name='player-winrate'
)
router.register(
    'hero-pickban',
    HeroPickBanViewSet,
    base_name='hero-pickban'
)
router.register('hero-dossiers', HeroDossierViewSet)
router.register('items', ItemViewSet)
router.register('matches', MatchViewSet)
router.register(
    'player-match-summary',
    PlayerMatchSummaryViewSet,
    base_name='player-match-summary'
)
router.register(
    'skillbuild',
    SkillBuildViewSet,
    base_name='skillbuild'
)
router.register('players', PlayerViewSet)
