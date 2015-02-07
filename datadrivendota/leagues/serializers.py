from rest_framework import serializers
from .models import League


class LeagueSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    def get_logo_url(self, obj):
        try:
            return obj.logo_image.url
        except ValueError:
            return ''

    class Meta:
        model = League
        fields = (
            'steam_id', 'display_name', 'display_description', 'logo_url'
        )
