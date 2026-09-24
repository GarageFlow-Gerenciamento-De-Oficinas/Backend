from typing import Any

from django.db import transaction

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from backend.core.mixins import ActiveStatusFilterMixin
from user.models import User
from user.serializers import UserSerializer
from user.services.invitation import create_user_invitation

@extend_schema_view(
    list=extend_schema(tags=["Usuários"]),
    retrieve=extend_schema(tags=["Usuários"]),
    create=extend_schema(tags=["Usuários"]),
    update=extend_schema(tags=["Usuários"]),
    partial_update=extend_schema(tags=["Usuários"]),
    destroy=extend_schema(tags=["Usuários"]),
)
class UserViewSet(ActiveStatusFilterMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[User]:
        queryset = super().get_queryset()

        return self.filter_by_active_status(queryset)

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        _, token = create_user_invitation(user)

        response_data = serializer.data
        response_data["invitation_token"] = token

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )
    
    @extend_schema(
        summary="Desativa um usuário",
        description=(
            "Desativa o usuário informado sem removê-lo fisicamente do banco de dados. "
            "Os dados históricos associados ao usuário são preservados."
        ),
        responses={
            204: OpenApiResponse(
                description="Usuário desativado com sucesso."
            ),
            404: OpenApiResponse(
                description="Usuário não encontrado."
            ),
        },
        tags=["Usuários"],
    )
    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = self.get_object()

        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(status=status.HTTP_204_NO_CONTENT)
