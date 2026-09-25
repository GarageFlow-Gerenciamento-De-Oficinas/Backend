from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView, Request

from user.serializers.activation import UserActivationSerializer, UserActivationResponseSerializer


class UserActivationView(APIView):
    permission_classes = [AllowAny]


    @extend_schema(
        request=UserActivationSerializer,
        responses=UserActivationResponseSerializer,
        summary="Ativa um usuário",
        description="Ativa um usuário através de um convite válido e define sua senha.",
        tags=["Autenticação"],
    )
    def post(self, request: Request) -> Response:
        serializer = UserActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Usuário ativado com sucesso."},
            status=status.HTTP_200_OK,
        )