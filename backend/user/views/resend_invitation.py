from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView, Request
from rest_framework.permissions import AllowAny

from user.services.invitation import resend_user_invitation_by_email
from user.serializers.invitation import ResendInvitationResponseSerializer, ResendInvitationSerializer

class ResendInvitationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=ResendInvitationSerializer,
        responses=ResendInvitationResponseSerializer,
        summary="Reenvia convite de ativação",
        description=(
            "Solicita o reenvio do convite de ativação para um usuário."
        ),
        tags=["Autenticação"],
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        serializer = ResendInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        resend_user_invitation_by_email(
            serializer.validated_data["email"],
        )

        return Response(
            {
                "detail": (
                    "Se o usuário estiver apto a receber um novo convite, "
                    "um novo convite será enviado."
                )
            },
            status=status.HTTP_200_OK,
        )