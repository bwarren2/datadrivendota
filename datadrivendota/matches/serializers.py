from rest_framework import serializers
from matches.models import Match, PlayerMatchSummary, SkillBuild, PickBan
from players.serializers import PlayerSerializer
from heroes.serializers import HeroSerializer
import six
from rest_framework.relations import RelatedField


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
        )


from heroes.models import Hero


class HeroStubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hero
        fields = ('steam_id',)


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
        # ordering = (,)
        fields = (
            'steam_id',
            'start_time',
            'radiant_win',
            'pickbans',
        )


class FastHeroStubSerializer(serializers.Serializer):
    steam_id = serializers.IntegerField()


class FastPickbanSerializer(serializers.Serializer):
    is_pick = serializers.BooleanField()
    team = serializers.IntegerField()
    order = serializers.IntegerField()
    hero = HeroStubSerializer()


class FastMatchPickBansSerializer(serializers.Serializer):

    steam_id = serializers.IntegerField()
    start_time = serializers.IntegerField()
    radiant_win = serializers.BooleanField()
    pickbans = FastPickbanSerializer(many=True, read_only=True)
