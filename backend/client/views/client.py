from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet

from backend.core.mixins import ActiveStatusFilterMixin
from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiParameter, extend_schema_view

from client.models import Client, Vehicle
from client.serializers import ClientSerializer, VehicleSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@extend_schema_view(
    list=extend_schema(tags=["Clientes"]),
    retrieve=extend_schema(tags=["Clientes"]),
    create=extend_schema(tags=["Clientes"]),
    update=extend_schema(tags=["Clientes"]),
    partial_update=extend_schema(tags=["Clientes"]),
    destroy=extend_schema(tags=["Clientes"]),
)
class ClientViewSet(ActiveStatusFilterMixin, ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        return self.filter_by_active_status(queryset)

    @extend_schema(
        summary="Desativa um cliente",
        description=(
            "Desativa o cliente informado sem removê-lo fisicamente do banco de dados. "
            "Os dados históricos associados ao cliente são preservados."
        ),
        responses={
            204: OpenApiResponse(
                description="Cliente desativado com sucesso."
            ),
            404: OpenApiResponse(
                description="Cliente não encontrado."
            ),
        },
        tags=["Clientes"],
    )
    def destroy(self, request, *args, **kwargs):
        client = self.get_object()

        client.is_active = False
        client.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Lista os veículos de um cliente",
        description=(
            "Retorna os veículos associados ao cliente informado. "
            "Por padrão, apenas veículos ativos são retornados."
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
            200: VehicleSerializer(many=True),
            404: OpenApiResponse(description="Cliente não encontrado."),
        },
        tags=["Veículos"]
    )

    @action(
        detail=True,
        methods=["get"],
        url_path="vehicles"
    )
    def vehicles(self, request, pk=None):
        client = self.get_object()
        
        vehicles = Vehicle.objects.filter(
            client=client
        )

        vehicles = self.filter_by_active_status(vehicles)

        serializer = VehicleSerializer(
            vehicles,
            many=True
        )

        return Response(serializer.data)