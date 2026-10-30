from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.validated_data
        response = Response({
            "access": tokens["access"]
        })

        response.set_cookie(
            key="garageflow_refresh",
            value=tokens["refresh"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/api/auth/",
            max_age=60 * 60 * 24
        )

        return response

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("garageflow_refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token não encontrado."},
                status=401,
            )

        serializer = TokenRefreshSerializer(
            data={"refresh": refresh_token}
        )

        serializer.is_valid(raise_exception=True)

        return Response({
            "access": serializer.validated_data["access"],
        })