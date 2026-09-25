from rest_framework import serializers

class ResendInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResendInvitationResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
