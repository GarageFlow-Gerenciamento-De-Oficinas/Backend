from rest_framework import serializers

from user.services.activation import activate_user, ActivationError

class UserActivationSerializer(serializers.Serializer):
    token = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def save(self):
        try:
            return activate_user(
                token = self.validated_data["token"],
                password= self.validated_data["password"]
            )
        except ActivationError as exc:
            raise serializers.ValidationError({
                "token": str(exc)
            })