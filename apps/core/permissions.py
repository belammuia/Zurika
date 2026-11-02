from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()


class RoleBasePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        required_rank = User.ROLE_HIERARCHY.get(
            self.required_role
        )

        if required_rank is None:
            return False

        return user.role_rank >= required_rank


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.CLIENT
        )


class IsOfficerOrAbove(RoleBasePermission):
    required_role = User.Role.OFFICER


class IsSeniorOfficer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == User.Role.SENIOR_OFFICER
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.role == User.Role.ADMIN
        )


class HasInsurerMembership(BasePermission):
    """
    Requires an active membership in an active insurer.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        return user.insurer_memberships.filter(
            is_active=True,
            insurer__is_active=True,
        ).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        insurer_id = getattr(obj, "insurer_id", None)

        if insurer_id is None and hasattr(obj, "claim"):
            insurer_id = obj.claim.insurer_id

        if insurer_id is None:
            return False

        return user.insurer_memberships.filter(
            insurer_id=insurer_id,
            is_active=True,
            insurer__is_active=True,
        ).exists()


class IsInsurerAdmin(BasePermission):
    """
    Requires an active administrator membership.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        return user.insurer_memberships.filter(
            role="admin",
            is_active=True,
            insurer__is_active=True,
        ).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        insurer_id = getattr(obj, "insurer_id", None)

        if insurer_id is None and hasattr(obj, "claim"):
            insurer_id = obj.claim.insurer_id

        if insurer_id is None:
            return False

        return user.insurer_memberships.filter(
            insurer_id=insurer_id,
            role="admin",
            is_active=True,
            insurer__is_active=True,
        ).exists()


class IsInsurerSeniorOfficer(BasePermission):
    """
    Requires an active senior claims officer membership
    in the object's insurer.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        return user.insurer_memberships.filter(
            role="senior_officer",
            is_active=True,
            insurer__is_active=True,
        ).exists()

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated:
            return False

        insurer_id = getattr(obj, "insurer_id", None)

        if insurer_id is None and hasattr(obj, "claim"):
            insurer_id = obj.claim.insurer_id

        if insurer_id is None:
            return False

        return user.insurer_memberships.filter(
            insurer_id=insurer_id,
            role="senior_officer",
            is_active=True,
            insurer__is_active=True,
        ).exists()