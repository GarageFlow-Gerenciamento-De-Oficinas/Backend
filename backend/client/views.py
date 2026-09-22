from rest_framework.viewsets import ModelViewSet

from .models import Client
from .serializers import ClientSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        is_active = self.request.query_params.get("active")

        if is_active is None:
            return queryset.filter(active=True)

        return queryset.filter(active= (is_active.lower() == "true"))

    def destroy(self, request, *args, **kwargs):
        client = self.get_object()

        client.active = False
        client.save(update_fields=["active"])
        return Response(status=status.HTTP_204_NO_CONTENT)