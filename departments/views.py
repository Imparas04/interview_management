from rest_framework import viewsets, permissions
from .models import Department
from .serializers import DepartmentSerializer
from accounts.permissions import IsAdmin


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    /api/departments/          GET (any authenticated user), POST (admin only)
    /api/departments/{id}/     GET, PUT, PATCH, DELETE (admin only for writes)

    Everyone who's logged in (HR, Interviewer, Candidate, Admin) can VIEW
    departments - e.g. a candidate needs to see department names when
    browsing jobs. Only Admin can create/edit/delete, per spec
    ("Admin should be able to add/edit/delete departments").
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdmin()]
        return [permissions.IsAuthenticated()]
