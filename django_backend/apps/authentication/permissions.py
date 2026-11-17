from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsBusinessApproved(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role in ['consumer', 'admin']:
            return True
        if request.user.role == 'store' and request.user.is_approved:
            return True
        return False
