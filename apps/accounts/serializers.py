
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Profile, OfficerProfile

User = get_user_model()


class CustomRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password],
    )

    first_name = serializers.CharField(
        max_length=65,
        write_only=True,
    )
    last_name = serializers.CharField(
        max_length=65,
        write_only=True,
    )

    role = serializers.ChoiceField(
        choices=[
            User.Role.CLIENT,
            User.Role.OFFICER,
            User.Role.SENIOR_OFFICER,
        ]
    )

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "role",
            "first_name",
            "last_name",
        ]

    @transaction.atomic
    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        role = validated_data["role"]

        user = (
            User.objects.create_custom_staff(**validated_data)
            if role in (User.Role.OFFICER, User.Role.SENIOR_OFFICER)
            else User.objects.create_user(**validated_data)
        )

        if role in (User.Role.OFFICER, User.Role.SENIOR_OFFICER):
            OfficerProfile.objects.create(
                officer=user,
                first_name=first_name,
                last_name=last_name,
                )
        else:
            Profile.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
            )

        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "role",
            "is_staff",
            "is_superuser",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CustomUserProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "user",
        ]

class AssignedOfficerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    title = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = ["name", "title"]

    def get_name(self, user):
        profile = getattr(user, "officer_profile", None)
        if not profile:
            return "Claims team"
        return f"{profile.first_name} {profile.last_name[:1]}.".strip()