from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    thumbshot_url = serializers.SerializerMethodField()
    mugshot_url = serializers.SerializerMethodField()

    def get_thumbshot_url(self, obj):
        return obj.thumbshot_image

    def get_mugshot_url(self, obj):
        return obj.mugshot_image

    class Meta:
        model = Item
        fields = (
            'steam_id', 'thumbshot_url', 'mugshot_url', 'internal_name', 'name'
            )
