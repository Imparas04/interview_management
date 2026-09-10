from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == request.user.Role.ADMIN)


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == request.user.Role.HR)


class IsInterviewer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == request.user.Role.INTERVIEWER)


class IsCandidate(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == request.user.Role.CANDIDATE)


class IsAdminOrHR(BasePermission):
    """Common combo - HR-facing endpoints Admin should also be able to hit."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in [request.user.Role.ADMIN, request.user.Role.HR])
