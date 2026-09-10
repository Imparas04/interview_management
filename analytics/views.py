from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from candidates.models import CandidateProfile
from applications.models import Application
from interviews.models import Interview
from accounts.permissions import IsAdminOrHR


class DashboardOverviewView(APIView):
    """
    GET /api/analytics/overview/    HR/Admin only.

    All numbers are computed here from the actual tables at request time -
    per spec, the backend/database is responsible for these statistics,
    never the frontend.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdminOrHR]

    def get(self, request):
        total_candidates = CandidateProfile.objects.count()
        shortlisted = Application.objects.filter(status=Application.Status.SHORTLISTED).count()
        interviews_scheduled = Interview.objects.filter(status=Interview.Status.SCHEDULED).count()
        selected = Application.objects.filter(status=Application.Status.SELECTED).count()
        rejected = Application.objects.filter(status=Application.Status.REJECTED).count()
        pending = Application.objects.exclude(
            status__in=[Application.Status.SELECTED, Application.Status.REJECTED]
        ).count()

        department_wise = list(
            Application.objects.values('job__department__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            "total_candidates": total_candidates,
            "shortlisted": shortlisted,
            "interviews_scheduled": interviews_scheduled,
            "selected": selected,
            "rejected": rejected,
            "pending": pending,
            "department_wise_candidates": [
                {"department": row['job__department__name'] or "Unassigned", "count": row['count']}
                for row in department_wise
            ],
        })


class CandidateDashboardSummaryView(APIView):
    """
    GET /api/analytics/candidate-summary/    candidate only - their own numbers.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != user.Role.CANDIDATE:
            return Response({"detail": "Candidates only."}, status=403)

        applications = Application.objects.filter(candidate__user=user)
        return Response({
            "applied_jobs": applications.count(),
            "shortlisted": applications.filter(status=Application.Status.SHORTLISTED).count(),
            "interviews": Interview.objects.filter(application__candidate__user=user).count(),
            "completed_interviews": Interview.objects.filter(
                application__candidate__user=user, status=Interview.Status.COMPLETED
            ).count(),
        })
