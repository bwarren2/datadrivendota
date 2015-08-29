from rest_framework import serializers, filters
from heroes.models import Hero, HeroDossier


class HeroSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        try:
            return obj.mugshot_url
        except ValueError:
            return ''
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name')

    class Meta:
        model = Hero
        fields = (
            'steam_id',
            'internal_name',
            'name',
            'image_url',
            'css_classes',
            'visible',
        )


class HeroDossierSerializer(serializers.ModelSerializer):
    hero = HeroSerializer()

    class Meta:
        model = HeroDossier
        exclude = ('id',)


class HeroWinrateSerializer(serializers.Serializer):
    hero = serializers.SerializerMethodField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    games = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(HeroWinrateSerializer, self).__init__(*args, **kwargs)
        self.heroes = {h.steam_id: h for h in Hero.objects.all()}

    def get_hero(self, obj):
        try:
            return HeroSerializer(self.heroes[obj['hero__steam_id']]).data
        except AttributeError:
            return ''

    class Meta:
        fields = (
            'hero',
            'wins',
            'losses',
            'games',
        )


class HeroPickBanSerializer(serializers.Serializer):
    hero = serializers.SerializerMethodField()
    picks = serializers.IntegerField()
    bans = serializers.IntegerField()
    pick_or_bans = serializers.IntegerField()

    def __init__(self, *args, **kwargs):
        super(HeroPickBanSerializer, self).__init__(*args, **kwargs)
        self.heroes = {h.steam_id: h for h in Hero.objects.all()}

    def get_hero(self, obj):
        try:
            return HeroSerializer(self.heroes[obj['hero__steam_id']]).data
        except AttributeError:
            return ''

    class Meta:
        fields = (
            'hero',
            'picks',
            'bans',
            'pick_or_bans',
        )


class HeroStubSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hero
        fields = ('steam_id',)


class FastHeroStubSerializer(serializers.Serializer):
    steam_id = serializers.IntegerField()
