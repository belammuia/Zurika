from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from .models import Vehicle, Policy
from .serializers import VehicleSerializer, PolicySerializer

from apps.core.permissions import IsAdmin

User = get_user_model()



class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdmin,
    ]
    http_method_names = [
        "get", "post", "put", "patch", "head", "options"
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.CLIENT:
            return Vehicle.objects.filter(owner=user)

        if user.role in [
            User.Role.OFFICER,
            User.Role.SENIOR_OFFICER,
            User.Role.ADMIN,
        ]:
            return Vehicle.objects.all()

        return Vehicle.objects.none()


class PolicyViewSet(viewsets.ModelViewSet):
    serializer_class = PolicySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdmin,
    ]
    http_method_names = [
        "get", "post", "put", "patch", "head", "options"
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role == User.Role.CLIENT:
            return Policy.objects.filter(user=user).select_related(
                "user", "vehicle"
            )

        if user.role in [
            User.Role.OFFICER,
            User.Role.SENIOR_OFFICER,
            User.Role.ADMIN,
        ]:
            return Policy.objects.all().select_related(
                "user", "vehicle"
            )

        return Policy.objects.none()
