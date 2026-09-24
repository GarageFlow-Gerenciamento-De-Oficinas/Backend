from typing import Any

from rest_framework import serializers

from user.models import User
from user.services.activation import activate_user, ActivationError

class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def save(self) -> User:
        try:
            return activate_user(
                token = self.validated_data["token"],
                password= self.validated_data["password"]
            )
        except ActivationError as exc:
            raise serializers.ValidationError({
                "token": str(exc)
            })

class UserActivationResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()