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


DEFAULT_SHORTLIST_THRESHOLD = 75.0


class AutoProcessApplicationsView(APIView):
    """
    POST /api/applications/auto-process/
    body: {"job_id": 1, "shortlist_threshold": 75}   ("shortlist_threshold" optional, defaults to 75)

    HR/Admin only. For every application on this job still in 'applied'
    status: extracts skills if missing, calculates the ATS score, moves the
    application through 'ats_analysis', then auto-shortlists or
    auto-rejects based on the threshold - all through the same enforced
    state machine as a manual status update, so nothing here bypasses
    transitions.py.

    Only touches applications currently in 'applied' - re-running this is
    safe and won't re-process candidates already moved further along.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def post(self, request):
        job_id = request.data.get('job_id')
        if not job_id:
            return Response({"detail": "job_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            threshold = float(request.data.get('shortlist_threshold', DEFAULT_SHORTLIST_THRESHOLD))
        except (TypeError, ValueError):
            return Response({"detail": "shortlist_threshold must be a number."}, status=status.HTTP_400_BAD_REQUEST)

        from jobs.models import JobRole
        from ats.models import ATSResult, CandidateSkill
        from ats.skill_extraction import extract_skills
        from ats.scoring import calculate_ats_score
        from resumes.models import Resume

        try:
            job = JobRole.objects.get(id=job_id)
        except JobRole.DoesNotExist:
            return Response({"detail": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        applications = Application.objects.filter(
            job=job, status=Application.Status.APPLIED
        ).select_related('resume', 'candidate__user')

        results = []
        shortlisted_count = 0
        rejected_count = 0
        skipped = []

        for application in applications:
            resume = application.resume

            if resume.parsing_status != Resume.ParsingStatus.SUCCESS:
                skipped.append({"application_id": application.id, "reason": "resume not successfully parsed"})
                continue

            # Extract skills now if this candidate has none yet for this resume.
            candidate_skill_names = list(application.candidate.skills.values_list('skill_name', flat=True))
            if not candidate_skill_names:
                candidate_skill_names = extract_skills(resume.parsed_text)
                application.candidate.skills.all().delete()
                CandidateSkill.objects.bulk_create([
                    CandidateSkill(candidate=application.candidate, skill_name=name, source_resume=resume)
                    for name in candidate_skill_names
                ])

            score_data = calculate_ats_score(resume, job, candidate_skill_names)
            ats_result, _ = ATSResult.objects.update_or_create(
                resume=resume, job=job, defaults=score_data
            )

            transition_application_status(application, Application.Status.ATS_ANALYSIS)

            if ats_result.overall_score >= threshold:
                transition_application_status(application, Application.Status.SHORTLISTED)
                shortlisted_count += 1
                new_status = Application.Status.SHORTLISTED
            else:
                transition_application_status(application, Application.Status.REJECTED)
                rejected_count += 1
                new_status = Application.Status.REJECTED

            results.append({
                "application_id": application.id,
                "candidate": application.candidate.user.username,
                "ats_score": ats_result.overall_score,
                "new_status": new_status,
            })

        return Response({
            "job_id": job.id,
            "threshold_used": threshold,
            "processed": len(results),
            "shortlisted": shortlisted_count,
            "rejected": rejected_count,
            "skipped": skipped,
            "results": results,
        }, status=status.HTTP_200_OK)
