from .serializers import PingRequestSerializer
from rest_framework import viewsets
from rest_framework.response import Response

from accounts.models import PingRequest


class PingRequestViewSet(viewsets.ModelViewSet):
    queryset = PingRequest.objects.all()
    paginate_by = 10
    serializer_class = PingRequestSerializer

    def list(self, serializer):

        return Response('No listing of these.')

    def retrieve(self, serializer):
        return Response('No listing of these.')

    def update(self, serializer):
        return Response('No updating of these.')

    def destroy(self, serializer):
        return Response('No destroying of these.  Nice try.')
