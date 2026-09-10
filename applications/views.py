from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Application
from .serializers import ApplicationSerializer, ApplicationCreateSerializer, StatusUpdateSerializer
from .transitions import transition_application_status
from accounts.permissions import IsCandidate, IsAdminOrHR
from candidates.models import CandidateProfile


class ApplicationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/applications/     candidate: own only; HR/Admin: all (filterable)
    POST /api/applications/     candidate only - apply to a job with a resume
    """
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job', 'status']

    def get_serializer_class(self):
        return ApplicationCreateSerializer if self.request.method == 'POST' else ApplicationSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsCandidate()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related('candidate__user', 'job__department', 'resume')
        if user.role == user.Role.CANDIDATE:
            return qs.filter(candidate__user=user)
        return qs

    def perform_create(self, serializer):
        candidate, _ = CandidateProfile.objects.get_or_create(user=self.request.user)
        application = serializer.save(candidate=candidate, status=Application.Status.APPLIED)

        from notifications.services import notify_role
        from django.contrib.auth import get_user_model
        User = get_user_model()
        notify_role(
            User.Role.HR,
            f"New candidate application received. Candidate: {candidate.user.username}, Job: {application.job.title}.",
            notif_type='application',
        )


class ApplicationDetailView(generics.RetrieveAPIView):
    """GET /api/applications/{id}/ - owner or HR/Admin/Interviewer."""
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Application.objects.select_related('candidate__user', 'job__department', 'resume')

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == user.Role.CANDIDATE and obj.candidate.user_id != user.id:
            self.permission_denied(self.request, message="Not allowed.")
        return obj


class ApplicationStatusUpdateView(APIView):
    """
    PATCH /api/applications/{id}/status/     body: {"status": "shortlisted"}
    HR/Admin only. Goes through transitions.py - an invalid transition
    (e.g. skipping from 'applied' straight to 'selected') returns 400 with
    a clear message instead of silently accepting any string.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def patch(self, request, pk):
        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            transition_application_status(application, serializer.validated_data['status'])
        except DjangoValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ApplicationSerializer(application).data, status=status.HTTP_200_OK)


class CandidateRankingView(APIView):
    """
    GET /api/applications/rank/?job=<job_id>

    HR/Admin only. Ranks all applications for a job by their ATSResult
    overall_score, descending - deterministic (ties broken by earliest
    application), never randomized. This is exactly the underlying data
    Phase 8's scoring already computed; ranking just orders and numbers it.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get(self, request):
        job_id = request.query_params.get('job')
        if not job_id:
            return Response({"detail": "job query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        from ats.models import ATSResult

        applications = Application.objects.filter(job_id=job_id).select_related(
            'candidate__user', 'job__department', 'resume'
        )

        # Build a lookup of resume_id -> overall_score for this job in one query,
        # instead of querying ATSResult once per application (N+1 avoidance).
        ats_scores = {
            r.resume_id: r.overall_score
            for r in ATSResult.objects.filter(job_id=job_id)
        }

        ranked = []
        for app in applications:
            ranked.append({
                "application_id": app.id,
                "candidate": app.candidate.user.username,
                "ats_score": ats_scores.get(app.resume_id),
                "department": app.job.department.name,
                "status": app.status,
                "applied_at": app.applied_at,
            })

        # Deterministic sort: unscored candidates (None) go last, not first/random.
        ranked.sort(key=lambda r: (r["ats_score"] is None, -(r["ats_score"] or 0), r["applied_at"]))

        for i, row in enumerate(ranked, start=1):
            row["rank"] = i
            del row["applied_at"]

        return Response(ranked, status=status.HTTP_200_OK)
