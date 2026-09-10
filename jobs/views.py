from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import JobRole
from .serializers import JobRoleSerializer
from accounts.permissions import IsAdminOrHR


class JobRoleViewSet(viewsets.ModelViewSet):
    """
    /api/jobs/          GET (all authenticated), POST (admin/HR only)
    /api/jobs/{id}/      GET, PUT, PATCH, DELETE (admin/HR only for writes)

    Candidates only ever see jobs with status='open' - HR/Admin see everything
    including drafts and closed jobs, since they need to manage the full list.
    """
    serializer_class = JobRoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['department', 'job_type', 'status']
    search_fields = ['title', 'location']

    def get_queryset(self):
        user = self.request.user
        qs = JobRole.objects.select_related('department').prefetch_related('required_skills')
        if user.is_authenticated and user.role in [user.Role.ADMIN, user.Role.HR]:
            return qs
        return qs.filter(status=JobRole.Status.OPEN)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrHR()]
        return [permissions.IsAuthenticated()]

    # Note: created_by is set inside JobRoleSerializer.create() using
    # self.context['request'].user - no perform_create() override needed,
    # since serializer.save() here takes no extra kwargs.
