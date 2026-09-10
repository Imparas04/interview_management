from rest_framework import generics, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import InterviewRound, Interview, InterviewFeedback
from .serializers import InterviewRoundSerializer, InterviewSerializer, InterviewFeedbackSerializer
from accounts.permissions import IsAdminOrHR, IsInterviewer
from notifications.services import notify


class InterviewRoundViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/interview-rounds/ - any authenticated user can view the round list."""
    queryset = InterviewRound.objects.all()
    serializer_class = InterviewRoundSerializer
    permission_classes = [permissions.IsAuthenticated]


class InterviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/interviews/    role-scoped (see get_queryset)
    POST /api/interviews/    HR/Admin only - conflict-checked in the serializer
    """
    serializer_class = InterviewSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'round', 'interviewer', 'application']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsAdminOrHR()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Interview.objects.select_related('application__candidate__user', 'application__job', 'round', 'interviewer')
        if user.role == user.Role.CANDIDATE:
            return qs.filter(application__candidate__user=user)
        if user.role == user.Role.INTERVIEWER:
            return qs.filter(interviewer=user)
        return qs  # HR, Admin see all

    def perform_create(self, serializer):
        interview = serializer.save()

        notify(
            recipient=interview.application.candidate.user,
            message=(
                f"Your interview has been scheduled. Round: {interview.round.name}, "
                f"Date: {interview.scheduled_date}, Time: {interview.scheduled_time}."
            ),
            notif_type='interview',
        )
        notify(
            recipient=interview.interviewer,
            message=(
                f"You have a new interview assigned. Candidate: "
                f"{interview.application.candidate.user.username}, Date: {interview.scheduled_date}."
            ),
            notif_type='interview',
        )


class InterviewDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/interviews/{id}/
    HR/Admin can update (reschedule, change status) - conflict-checked
    again on update since date/time/interviewer might change.
    """
    serializer_class = InterviewSerializer
    queryset = Interview.objects.select_related('application__candidate__user', 'application__job', 'round', 'interviewer')

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsAdminOrHR()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == user.Role.CANDIDATE and obj.application.candidate.user_id != user.id:
            self.permission_denied(self.request, message="Not allowed.")
        if user.role == user.Role.INTERVIEWER and obj.interviewer_id != user.id:
            self.permission_denied(self.request, message="Not allowed.")
        return obj


class InterviewFeedbackCreateView(generics.CreateAPIView):
    """
    POST /api/interview-feedback/    interviewer only, must be the
    interviewer assigned to that specific interview.
    Marks the interview COMPLETED automatically (see serializer.create()).
    """
    serializer_class = InterviewFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsInterviewer]

    def perform_create(self, serializer):
        interview = serializer.validated_data['interview']
        if interview.interviewer_id != self.request.user.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only submit feedback for your own assigned interviews.")
        serializer.save()


class InterviewFeedbackListView(generics.ListAPIView):
    """
    GET /api/interview-feedback/?interview=<id>
    HR/Admin/Interviewer only - "HR should be able to see feedback",
    candidates see their result via application status, not raw scores.
    """
    serializer_class = InterviewFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['interview']

    def get_queryset(self):
        user = self.request.user
        if user.role == user.Role.CANDIDATE:
            return InterviewFeedback.objects.none()
        qs = InterviewFeedback.objects.select_related('interview')
        if user.role == user.Role.INTERVIEWER:
            return qs.filter(interview__interviewer=user)
        return qs
