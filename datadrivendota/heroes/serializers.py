from rest_framework import serializers, filters
from heroes.models import Hero, HeroDossier


class HeroSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        try:
            return obj.mugshot.url
        except ValueError:
            return ''
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name')

    class Meta:
        model = Hero
        fields = ('steam_id', 'internal_name', 'name', 'image_url', 'visible')


class HeroDossierSerializer(serializers.ModelSerializer):
    hero = HeroSerializer()

    class Meta:
        model = HeroDossier
        exclude = ('id',)
