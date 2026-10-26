
from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Claim, SupportingDocument
from .serializers import (
    ClaimReadSerializer,
    ClaimSubmissionSerializer,
    SupportingDocumentSerializer,
)
from apps.core.permissions import IsClient


class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
        IsClient,
    ]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        user = self.request.user

        if user.role == "client":
            return Claim.objects.filter(
                user=user
            ).select_related("user", "vehicle")

        if user.role in [
            "claims_officer",
            "senior_officer",
            "admin",
        ]:
            return Claim.objects.all().select_related(
                "user", "vehicle"
            )

        return Claim.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return ClaimSubmissionSerializer

        return ClaimReadSerializer


class SupportingDocumentViewSet(viewsets.ModelViewSet):
    queryset = SupportingDocument.objects.all()
    serializer_class = SupportingDocumentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsClient,
    ]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return SupportingDocument.objects.filter(
            claim__user=self.request.user
        ).select_related("claim")
