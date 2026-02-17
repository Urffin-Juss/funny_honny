from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import UserRole


class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role in {UserRole.OWNER, UserRole.ADMIN}


class IsOwnerOrAdminWriteElseRead(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in {UserRole.OWNER, UserRole.ADMIN}


class IsTaskVisibleToUser(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        if request.user.role in {UserRole.OWNER, UserRole.ADMIN}:
            return True
        return obj.assignee_id == request.user.id
