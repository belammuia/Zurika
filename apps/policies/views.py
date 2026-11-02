from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from .models import Vehicle, Policy
from .serializers import VehicleSerializer, PolicySerializer

from apps.core.permissions import IsAdmin

User = get_user_model()



class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    http_method_names = [
        "get", "post", "put", "patch", "head", "options"
    ]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update"):
            return [permissions.IsAuthenticated(), IsAdmin()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        qs = Vehicle.objects.select_related("owner")

        if user.role == User.Role.CLIENT:
            return qs.filter(owner=user)

        if user.role in [
            User.Role.OFFICER,
            User.Role.SENIOR_OFFICER,
            User.Role.ADMIN,
        ]:
            insurer_ids = user.insurer_memberships.filter(
                is_active=True,
                insurer__is_active=True,
            ).values_list("insurer_id", flat=True)

            return qs.filter(
                policies__insurer_id__in=insurer_ids
            ).distinct()

        return Vehicle.objects.none()


class PolicyViewSet(viewsets.ModelViewSet):
    serializer_class = PolicySerializer
    http_method_names = [
        "get", "post", "put", "patch", "head", "options"
    ]

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update"):
            return [permissions.IsAuthenticated(), IsAdmin()]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        qs = Policy.objects.select_related(
            "user",
            "vehicle",
            "insurer",
        )

        if user.role == User.Role.CLIENT:
            return qs.filter(user=user)

        if user.role in [
            User.Role.OFFICER,
            User.Role.SENIOR_OFFICER,
            User.Role.ADMIN,
        ]:
            insurer_ids = user.insurer_memberships.filter(
                is_active=True,
                insurer__is_active=True,
            ).values_list("insurer_id", flat=True)

            return qs.filter(insurer_id__in=insurer_ids)

        return Policy.objects.none()