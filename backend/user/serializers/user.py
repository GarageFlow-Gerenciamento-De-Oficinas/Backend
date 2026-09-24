from typing import Any

from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "address",
            "phone",
            "is_active",
            "activated_at",
            "first_name",
            "last_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "activated_at",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data: dict[str, Any]) -> User:
        user = User.objects.create_user(
            password=None,
            **validated_data
        )
        return user