from rest_framework import serializers
from matches.models import (
    Match, PlayerMatchSummary, SkillBuild, PickBan, CombatLog, StateLog
)
from players.serializers import PlayerSerializer
from heroes.serializers import HeroSerializer
import six
from rest_framework.relations import RelatedField

from heroes.serializers import FastHeroStubSerializer, HeroStubSerializer


class MyStringRelatedField(RelatedField):

    """A read only field that represents its targets using unicode."""

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super(MyStringRelatedField, self).__init__(**kwargs)

    def to_representation(self, value):
        if value.name is None:
            return ''
        else:
            return six.text_type(value)


class MatchSerializer(serializers.ModelSerializer):

    radiant_team = MyStringRelatedField()
    dire_team = MyStringRelatedField()

    class Meta:
        model = Match
        fields = (
            'steam_id',
            'start_time',
            'duration',
            'radiant_win',
            'skill',
            'radiant_team',
            'dire_team',
        )


class SkillBuildSerializer(serializers.ModelSerializer):

    class Meta:
        model = SkillBuild
        fields = (
            'ability',
            'time',
            'level',
        )


class PlayerMatchSummarySerializer(serializers.ModelSerializer):
    player = PlayerSerializer()
    hero = HeroSerializer()
    match = MatchSerializer()
    skillbuild = serializers.SerializerMethodField()

    def get_skillbuild(self, obj):
        return [
            SkillBuildSerializer(x).data for x in obj.skillbuild_set.all()
        ]

    class Meta:
        model = PlayerMatchSummary
        fields = (
            'id',
            'kills',
            'deaths',
            'assists',
            'last_hits',
            'denies',
            'gold',
            'gold_per_min',
            'xp_per_min',
            'hero_damage',
            'hero_healing',
            'tower_damage',
            'level',
            'is_win',
            'gold_total',
            'xp_total',
            'kda2',
            'side',
            'player',
            'hero',
            'match',
            'skillbuild',
            'replay_shard',
        )


class PickbanSerializer(serializers.ModelSerializer):
    hero = HeroStubSerializer()

    class Meta:
        model = PickBan
        exclude = ('match', 'id',)
        ordering = ('order',)


class MatchPickBansSerializer(serializers.ModelSerializer):

    pickbans = PickbanSerializer(
        source='pickban_set', many=True, read_only=True
    )

    class Meta:
        model = Match
        fields = (
            'steam_id',
            'start_time',
            'radiant_win',
            'pickbans',
        )


class FastPickbanSerializer(serializers.Serializer):
    is_pick = serializers.BooleanField()
    team = serializers.IntegerField()
    order = serializers.IntegerField()
    hero = FastHeroStubSerializer()


class FastMatchPickBansSerializer(serializers.Serializer):

    steam_id = serializers.IntegerField()
    start_time = serializers.IntegerField()
    radiant_win = serializers.BooleanField()
    duration = serializers.IntegerField()
    radiant_team = serializers.CharField()
    dire_team = serializers.CharField()
    pickbans = FastPickbanSerializer(many=True, read_only=True)


class CombatLogSerializer(serializers.Serializer):

    kills = serializers.URLField(
        read_only=True, source='kills.url'
    )
    deaths = serializers.URLField(
        read_only=True, source='deaths.url'
    )
    last_hits = serializers.URLField(
        read_only=True, source='last_hits.url'
    )
    xp = serializers.URLField(
        read_only=True, source='xp.url'
    )
    healing = serializers.URLField(
        read_only=True, source='healing.url'
    )
    hero_dmg_taken = serializers.URLField(
        read_only=True, source='hero_dmg_taken.url'
    )
    hero_dmg_dealt = serializers.URLField(
        read_only=True, source='hero_dmg_dealt.url'
    )
    other_dmg_taken = serializers.URLField(
        read_only=True, source='other_dmg_taken.url'
    )
    other_dmg_dealt = serializers.URLField(
        read_only=True, source='other_dmg_dealt.url'
    )
    all_income = serializers.URLField(
        read_only=True, source='all_income.url'
    )
    earned_income = serializers.URLField(
        read_only=True, source='earned_income.url'
    )
    building_income = serializers.URLField(
        read_only=True, source='building_income.url'
    )
    courier_kill_income = serializers.URLField(
        read_only=True, source='courier_kill_income.url'
    )
    creep_kill_income = serializers.URLField(
        read_only=True, source='creep_kill_income.url'
    )
    hero_kill_income = serializers.URLField(
        read_only=True, source='hero_kill_income.url'
    )
    roshan_kill_income = serializers.URLField(
        read_only=True, source='roshan_kill_income.url'
    )
    buyback_expense = serializers.URLField(
        read_only=True, source='buyback_expense.url'
    )
    death_expense = serializers.URLField(
        read_only=True, source='death_expense.url'
    )
    hero_xp = serializers.URLField(
        read_only=True, source='hero_xp.url'
    )
    playermatchsummary = PlayerMatchSummarySerializer()

    class Meta:
        model = CombatLog


class StateLogSerializer(serializers.Serializer):

    agility = serializers.URLField(
        read_only=True, source='agility.url'
    )
    agility_total = serializers.URLField(
        read_only=True, source='agility_total.url'
    )
    strength = serializers.URLField(
        read_only=True, source='strength.url'
    )
    strength_total = serializers.URLField(
        read_only=True, source='strength_total.url'
    )
    intelligence = serializers.URLField(
        read_only=True, source='intelligence.url'
    )
    intelligence_total = serializers.URLField(
        read_only=True, source='intelligence_total.url'
    )
    damage = serializers.URLField(
        read_only=True, source='damage.url'
    )
    damage_taken = serializers.URLField(
        read_only=True, source='damage_taken.url'
    )
    healing = serializers.URLField(
        read_only=True, source='healing.url'
    )
    health = serializers.URLField(
        read_only=True, source='health.url'
    )
    mana = serializers.URLField(
        read_only=True, source='mana.url'
    )
    kills = serializers.URLField(
        read_only=True, source='kills.url'
    )
    deaths = serializers.URLField(
        read_only=True, source='deaths.url'
    )
    assists = serializers.URLField(
        read_only=True, source='assists.url'
    )
    items = serializers.URLField(
        read_only=True, source='items.url'
    )
    last_hits = serializers.URLField(
        read_only=True, source='last_hits.url'
    )
    denies = serializers.URLField(
        read_only=True, source='denies.url'
    )
    misses = serializers.URLField(
        read_only=True, source='misses.url'
    )
    lifestate = serializers.URLField(
        read_only=True, source='lifestate.url'
    )
    magic_resist_pct = serializers.URLField(
        read_only=True, source='magic_resist_pct.url'
    )
    armor = serializers.URLField(
        read_only=True, source='armor.url'
    )
    recent_damage = serializers.URLField(
        read_only=True, source='recent_damage.url'
    )
    respawn_time = serializers.URLField(
        read_only=True, source='respawn_time.url'
    )
    roshan_kills = serializers.URLField(
        read_only=True, source='roshan_kills.url'
    )
    nearby_creep_deaths = serializers.URLField(
        read_only=True, source='nearby_creep_deaths.url'
    )
    shared_gold = serializers.URLField(
        read_only=True, source='shared_gold.url'
    )
    reliable_gold = serializers.URLField(
        read_only=True, source='reliable_gold.url'
    )
    total_earned_gold = serializers.URLField(
        read_only=True, source='total_earned_gold.url'
    )
    unreliable_gold = serializers.URLField(
        read_only=True, source='unreliable_gold.url'
    )
    creep_kill_gold = serializers.URLField(
        read_only=True, source='creep_kill_gold.url'
    )
    hero_kill_gold = serializers.URLField(
        read_only=True, source='hero_kill_gold.url'
    )
    income_gold = serializers.URLField(
        read_only=True, source='income_gold.url'
    )
    tower_kills = serializers.URLField(
        read_only=True, source='tower_kills.url'
    )
    xp = serializers.URLField(
        read_only=True, source='xp.url'
    )
    position = serializers.URLField(
        read_only=True, source='position.url'
    )
    playermatchsummary = PlayerMatchSummarySerializer()

    class Meta:
        model = StateLog
