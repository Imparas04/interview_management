from rest_framework import generics, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import CandidateProfile
from .serializers import CandidateProfileSerializer
from accounts.permissions import IsCandidate


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
