from rest_framework import serializers
from datetime import datetime

from client.models import Vehicle

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "id",
            "client",
            "plate",
            "brand",
            "model",
            "year",
            "color",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_plate(self, value):
        return value.replace("-", "").replace(" ", "").upper()

    def validate_year(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError(
                "O ano do veículo deve conter 4 dígitos."
            )

        year = int(value)
        current_year = datetime.now().year

        if year > current_year + 1:
            raise serializers.ValidationError(
                "O ano do veículo não pode ser superior ao próximo ano."
            )

        return value