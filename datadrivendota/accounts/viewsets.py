from .serializers import MatchRequestSerializer
from rest_framework import viewsets

from accounts.models import MatchRequest


class MatchRequestViewSet(viewsets.ModelViewSet):
    queryset = MatchRequest.objects.all()
    paginate_by = 10
    serializer_class = MatchRequestSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(requester=user)
