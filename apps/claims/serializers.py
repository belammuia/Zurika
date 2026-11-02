
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.policies.models import Policy
from .models import Claim, ClaimPolicy, SupportingDocument
from .services import triage_claim, process_claim, has_required_documents
from .routing import assign_claim, NoAvailableOfficerError
from .image_validation import (
    ImageVerdict, validate_vehicle_image
)
from apps.accounts.serializers import AssignedOfficerSerializer

class ClaimSubmissionSerializer(serializers.ModelSerializer):
    documents = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = Claim
        fields = [
            "id",
            "vehicle",
            "incident_date",
            "description",
            "estimated_cost",
            "vehicles_involved",
            "has_injury",
            "third_party_involved",
            "severe_structural_damage",
            "documents",
        ]
        read_only_fields = ["id"]

    def validate_estimated_cost(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Estimated cost must be greater than zero."
            )
        return value

    def validate_incident_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError(
                "Incident date cannot be in the future."
            )
        return value

    def validate_vehicles_involved(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "At least one vehicle must be involved."
            )
        return value

    def validate(self, attrs):
        request = self.context["request"]
        vehicle = attrs["vehicle"]
        incident_date = attrs["incident_date"]

        if vehicle.owner_id != request.user.id:
            raise serializers.ValidationError({
                "vehicle": (
                    "You can only submit claims for your own vehicle."
                )
            })

        eligible_policies = Policy.objects.filter(
            vehicle=vehicle,
            user=request.user,
            status=Policy.Status.ACTIVE,
            start_date__lte=incident_date,
            end_date__gte=incident_date,
            insurer__is_active=True,
            insurer__isnull=False,
        )

        if not eligible_policies.exists():
            raise serializers.ValidationError({
                "vehicle": (
                    "No active policy from an active insurer covers "
                    "this vehicle on the incident date."
                )
            })

        insurer_ids = set(
            eligible_policies.values_list("insurer_id", flat=True)
        )

        if len(insurer_ids) != 1:
            raise serializers.ValidationError({
                "vehicle": (
                    "All eligible policies must belong to the same insurer."
                )
            })

        return attrs

    def validate_documents(self, files):
        for index, uploaded_file in enumerate(files):
            verdict = validate_vehicle_image(uploaded_file)

            if verdict == ImageVerdict.INVALID:
                raise serializers.ValidationError(
                    f"Photo {index + 1} is invalid. "
                    "Please upload an appropriate vehicle image."
                )

            if verdict == ImageVerdict.UNCERTAIN:
                raise serializers.ValidationError(
                    "Image cannot be resolved. "
                    "Please resubmit a clear image."
                )

        return files

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        uploaded_files = validated_data.pop("documents", [])

        # Resolve eligible policies again inside the transaction.
        policies = list(
            Policy.objects.select_for_update()
            .filter(
                vehicle=validated_data["vehicle"],
                user=request.user,
                status=Policy.Status.ACTIVE,
                start_date__lte=validated_data["incident_date"],
                end_date__gte=validated_data["incident_date"],
                insurer__is_active=True,
                insurer__isnull=False,
            )
            .select_related("insurer")
        )

        insurer_ids = {policy.insurer_id for policy in policies}

        if not policies or len(insurer_ids) != 1:
            raise serializers.ValidationError({
                "vehicle": (
                    "Eligible policies must belong to exactly one "
                    "active insurer."
                )
            })

        insurer_id = next(iter(insurer_ids))

        claim = Claim.objects.create(
            user=request.user,
            insurer_id=insurer_id,
            **validated_data,
        )

        ClaimPolicy.objects.bulk_create([
            ClaimPolicy(
                claim=claim,
                policy=policy,
                vehicle=claim.vehicle,
            )
            for policy in policies
        ])

        claim.multi_policy_flag = len(policies) > 1
        claim.save(update_fields=["multi_policy_flag"])

        for uploaded_file in uploaded_files:
            SupportingDocument.objects.create(
                claim=claim,
                document_type="accident_photos",
                file=uploaded_file,
            )

        if not has_required_documents(claim):
            claim.status = Claim.Status.AWAITING_INFORMATION
            claim.save(update_fields=["status"])
            return claim

        return process_claim(claim)

class ClaimReadSerializer(serializers.ModelSerializer):
    assigned_officer = AssignedOfficerSerializer(read_only=True)
    can_decide = serializers.SerializerMethodField()
    payout_status = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            "id",
            "user",
            "vehicle",
            "claim_date",
            "incident_date",
            "description",
            "severity",
            "priority",
            "status",
            "estimated_cost",
            "vehicles_involved",
            "has_injury",
            "third_party_involved",
            "severe_structural_damage",
            "queue",
            "assigned_officer",
            "multi_policy_flag",
            "decision_source",
            "decision_reason",
            "can_decide",
            "payout_status",
        ]
        read_only_fields = fields

    def get_can_decide(self, claim):
        request = self.context.get("request")
        return bool(
            request
            and claim.assigned_officer_id == request.user.id
            and claim.status == Claim.Status.SUBMITTED
            )
    
    def get_payout_status(self, claim):
        payout = getattr(claim, "payout", None)
        return payout.status if payout else None

        
class SupportingDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportingDocument
        fields = [
            "id",
            "claim",
            "document_type",
            "file",
            "uploaded_at",
        ]
        read_only_fields = ["id", "uploaded_at"]

    def validate_claim(self, claim):
        request = self.context["request"]

        if claim.user_id != request.user.id:
            raise serializers.ValidationError(
                "You can only upload documents for your own claims."
            )

        return claim

    def validate_document_type(self, value):
        allowed_types = {"accident_photos"}

        if value not in allowed_types:
            raise serializers.ValidationError(
                "Unsupported document type."
            )
        return value
    
    def validate_file(self, uploaded_file):
        verdict = validate_vehicle_image(uploaded_file)
        if verdict == ImageVerdict.INVALID:
                raise serializers.ValidationError(
                    f"photo that has been uploaded is invalid. Upload an appropriate vehicle image please"
                )
        if verdict == ImageVerdict.UNCERTAIN:
                raise serializers.ValidationError(
                    "Image cannot be resolved, please resubmit another clear image"
                )

        return uploaded_file

    @transaction.atomic
    def create(self, validated_data):
        document = SupportingDocument.objects.create(**validated_data)
        claim = document.claim

        if claim.status != Claim.Status.AWAITING_INFORMATION:
            return document

        if not has_required_documents(claim):
            return document

        claim.status = Claim.Status.SUBMITTED
        claim.save(update_fields=["status"])

        process_claim(claim)

        return document

class ClaimReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(
        choices=[Claim.Status.APPROVED, Claim.Status.REJECTED]
    )
    reason = serializers.CharField(max_length=255)
