from django.db import transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from user.models import User
from user.serializers import UserSerializer
from user.services.invitation import create_user_invitation


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        invitation, token = create_user_invitation(user)

        response_data = serializer.data
        response_data["invitation_token"] = token

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
        )

