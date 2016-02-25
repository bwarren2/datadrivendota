from rest_framework import serializers
from matches.models import Match, PlayerMatchSummary, SkillBuild, PickBan
from players.serializers import PlayerSerializer
from heroes.serializers import HeroSerializer, AbilitySerializer
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
    ability = AbilitySerializer()

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


class ParseShardSerializer(serializers.Serializer):
    css_classes = serializers.CharField(max_length=200)
    name = serializers.CharField(max_length=200)
    dataslice = serializers.SerializerMethodField()
    match_id = serializers.SerializerMethodField()

    def get_match_id(self, obj):
        return str(obj.match_id)

    def get_dataslice(self, obj):
        return str(obj.dataslice)


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
