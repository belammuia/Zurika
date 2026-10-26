from rest_framework import serializers

from .models import Vehicle, Policy


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["id", "owner", "name", "registration_number"]
        read_only_fields = ["id"]

    def validate_registration_number(self, value):
        value = value.strip().upper()

        queryset = Vehicle.objects.filter(
            registration_number__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "A vehicle with this registration number already exists."
            )

        return value


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = [
            "id",
            "user",
            "vehicle",
            "policy_number",
            "policy_type",
            "status",
            "start_date",
            "end_date",
            "insurer_name",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = attrs.get(
            "user",
            self.instance.user if self.instance else None,
        )
        vehicle = attrs.get(
            "vehicle",
            self.instance.vehicle if self.instance else None,
        )
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None,
        )
        end_date = attrs.get(
            "end_date",
            self.instance.end_date if self.instance else None,
        )

        if user and vehicle and vehicle.owner_id != user.pk:
            raise serializers.ValidationError({
                "vehicle": (
                    "The selected vehicle must belong to "
                    "the selected client."
                )
            })

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        return attrs

