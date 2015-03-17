from rest_framework import serializers
from heroes.models import Hero


class HeroSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        try:
            return obj.mugshot.url
        except ValueError:
            return ''

    class Meta:
        model = Hero
        fields = ('steam_id', 'internal_name', 'name', 'image_url')
