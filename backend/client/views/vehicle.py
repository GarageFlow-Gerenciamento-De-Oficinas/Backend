from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from backend.core.mixins import ActiveStatusFilterMixin
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter, extend_schema_view

from client.models import Vehicle
from client.serializers import VehicleSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@extend_schema_view(
    list=extend_schema(tags=["Veículos"]),
    retrieve=extend_schema(tags=["Veículos"]),
    create=extend_schema(tags=["Veículos"]),
    update=extend_schema(tags=["Veículos"]),
    partial_update=extend_schema(tags=["Veículos"]),
    destroy=extend_schema(tags=["Veículos"]),
)
class VehicleViewSet(ActiveStatusFilterMixin, ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        return self.filter_by_active_status(queryset)


    @extend_schema(
        summary="Desativa um veiculo",
        description=(
            "Desativa o veiculo informado sem removê-lo fisicamente do banco de dados. "
            "Os dados históricos associados ao veiculo são preservados."
        ),
        parameters=[
            OpenApiParameter(
                name="show",
                description="Define quais veículos serão retornados.",
                required=False,
                type=str,
                enum=["active", "not_active", "all"],
            ),
        ],
        responses={
            204: OpenApiResponse(
                description="Veiculo desativado com sucesso."
            ),
            404: OpenApiResponse(
                description="Veiculo não encontrado."
            ),
        },
        tags=["Veículos"],
    )
    def destroy(self, request, *args, **kwargs):
        vehicle = self.get_object()

        vehicle.is_active = False
        vehicle.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)