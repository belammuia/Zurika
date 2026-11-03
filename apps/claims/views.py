
from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Claim, SupportingDocument
from .serializers import (
    ClaimReadSerializer,
    ClaimSubmissionSerializer,
    SupportingDocumentSerializer,
    ClaimReviewSerializer
)
from apps.core.permissions import IsClient, IsOfficerOrAbove
from .services import review_claim
from rest_framework.decorators import action
from rest_framework.response import Response

class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action in ("review", "assigned"):
            return [permissions.IsAuthenticated(), IsOfficerOrAbove()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsClient()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        qs = Claim.objects.select_related(
            "user",
            "vehicle",
            "insurer",
            # "assigned_officer__profile",
        )

        if user.role == "client":
            return qs.filter(user=user)

        if user.role in ("claims_officer", "senior_officer", "admin"):
            insurer_ids = user.insurer_memberships.filter(
                is_active=True,
                insurer__is_active=True,
            ).values_list("insurer_id", flat=True)

            return qs.filter(insurer_id__in=insurer_ids)

        return Claim.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return ClaimSubmissionSerializer
        return ClaimReadSerializer

    @action(detail=False, methods=["get"])
    def assigned(self, request):
        claims = self.get_queryset().filter(assigned_officer=request.user)
        serializer = self.get_serializer(claims, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        claim = self.get_object()

        serializer = ClaimReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claim = review_claim(
            claim,
            request.user,
            serializer.validated_data["decision"],
            serializer.validated_data["reason"],
        )
        return Response(
            ClaimReadSerializer(claim, context={"request": request}).data
        )


class SupportingDocumentViewSet(viewsets.ModelViewSet):
    queryset = SupportingDocument.objects.all()
    serializer_class = SupportingDocumentSerializer
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    http_method_names = ["get", "post", "head", "options"]

    def get_permissions(self):
        if self.action == "create":
            return [
                permissions.IsAuthenticated(),
                IsClient(),
            ]

        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        qs = SupportingDocument.objects.select_related(
            "claim",
            "claim__insurer",
            "claim__user",
        )

        if user.role == "client":
            return qs.filter(claim__user=user)

        if user.role in ("claims_officer", "senior_officer", "admin"):
            insurer_ids = user.insurer_memberships.filter(
                is_active=True,
                insurer__is_active=True,
            ).values_list("insurer_id", flat=True)

            return qs.filter(claim__insurer_id__in=insurer_ids)

        return SupportingDocument.objects.none()