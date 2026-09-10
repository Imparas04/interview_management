from rest_framework import generics, permissions, viewsets
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer
from accounts.permissions import IsCandidate, IsAdminOrHR


class MyCandidateProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT/PATCH /api/candidates/me/  - candidate-only.
    Auto-creates the profile on first GET so the frontend never has to
    handle a "profile doesn't exist yet" 404 case separately from a normal
    "profile exists, here it is" case.
    """
    permission_classes = [permissions.IsAuthenticated, IsCandidate]
    serializer_class = CandidateProfileSerializer

    def get_object(self):
        profile, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        return profile


class CandidateProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/candidates/           list (HR/Admin/Interviewer only)
    GET /api/candidates/{id}/      detail

    Read-only on purpose - HR/Interviewer review candidates but never edit
    a candidate's own profile data; only the candidate can, via /me/.
    """
    queryset = CandidateProfile.objects.select_related('user', 'recommended_department')
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['recommended_department']
    search_fields = ['user__username', 'user__email']

    def get_permissions(self):
        # Only HR/Admin/Interviewer may browse the candidate list - a
        # candidate should never see another candidate's profile through
        # this endpoint (they only ever get their own, via /me/).
        user = self.request.user
        if user.is_authenticated and user.role == user.Role.CANDIDATE:
            self.permission_denied(self.request, message="Candidates cannot list other candidate profiles.")
        return super().get_permissions()


class CandidateSearchView(generics.ListAPIView):
    """
    GET /api/candidates/search/

    Advanced multi-criteria search across candidate name/email, skills,
    department, job/application status, and ATS score - the fields
    explicitly listed in the spec's search & filtering requirement.
    HR/Admin only.

    Query params (all optional, combinable):
      name, email, skill, department, job, min_ats_score, application_status

    Example:
      /api/candidates/search/?department=3&min_ats_score=80&skill=Python
    """
    serializer_class = CandidateProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get_queryset(self):
        qs = CandidateProfile.objects.select_related('user', 'recommended_department').distinct()
        params = self.request.query_params

        name = params.get('name')
        if name:
            qs = qs.filter(user__username__icontains=name)

        email = params.get('email')
        if email:
            qs = qs.filter(user__email__icontains=email)

        skill = params.get('skill')
        if skill:
            qs = qs.filter(skills__skill_name__iexact=skill)

        department = params.get('department')
        if department:
            qs = qs.filter(recommended_department_id=department)

        job = params.get('job')
        if job:
            qs = qs.filter(applications__job_id=job)

        application_status = params.get('application_status')
        if application_status:
            qs = qs.filter(applications__status=application_status)

        min_ats_score = params.get('min_ats_score')
        if min_ats_score:
            from ats.models import ATSResult
            candidate_ids = ATSResult.objects.filter(
                overall_score__gte=float(min_ats_score)
            ).values_list('resume__candidate_id', flat=True)
            qs = qs.filter(id__in=candidate_ids)

        return qs
