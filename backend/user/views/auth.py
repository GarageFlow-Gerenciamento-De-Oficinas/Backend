from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

@method_decorator(csrf_protect, name="dispatch")
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

@method_decorator(csrf_protect, name="dispatch")
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("garageflow_refresh")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token não encontrado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(
            data={"refresh": refresh_token}
        )

        serializer.is_valid(raise_exception=True)

        return Response({
            "access": serializer.validated_data["access"],
        })

@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("garageflow_refresh")

        response = Response(
            {"detail": "Logout realizado com sucesso."},
            status= status.HTTP_200_OK
        )

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                pass

        response.delete_cookie(
            key="garageflow_refresh",
            path="/api/auth/",
            samesite="Lax",
        )

        return response

@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({"detail": "CSRF cookie ready."})