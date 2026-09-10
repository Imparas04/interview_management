from datetime import datetime, timedelta
from django.conf import settings
from django.db import models
from applications.models import Application


class InterviewRound(models.Model):
    """
    Master list of round types (HR Screening, Technical Interview, etc.)
    with an explicit order. Kept as its own table (not a hardcoded choices
    list on Interview) so HR/Admin could add a custom round later without
    a code change - matches the "5 round" list in the spec being a
    starting point, not a hard limit.
    """
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.name}"


class Interview(models.Model):
    """
    One scheduled interview instance for one application, at one round.
    A candidate going through 3 rounds ends up with 3 Interview rows
    (not one row mutated 3 times) - this is what makes feedback history
    per round automatic (see InterviewFeedback below).
    """

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        RESCHEDULED = 'rescheduled', 'Rescheduled'
        CANCELLED = 'cancelled', 'Cancelled'

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    round = models.ForeignKey(InterviewRound, on_delete=models.PROTECT, related_name='interviews')
    interviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='assigned_interviews')

    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location_or_link = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def get_time_range(self):
        start = datetime.combine(self.scheduled_date, self.scheduled_time)
        end = start + timedelta(minutes=self.duration_minutes)
        return start, end

    def __str__(self):
        return f"{self.application.candidate.user.username} - {self.round.name} on {self.scheduled_date}"


class InterviewFeedback(models.Model):
    """
    OneToOne on Interview - exactly one feedback per interview INSTANCE.
    Because each round is its own Interview row, feedback is never
    overwritten across rounds; a candidate's 3rd-round feedback simply
    lives on a different Interview/InterviewFeedback pair than round 1.
    """

    class Recommendation(models.TextChoices):
        NEXT_ROUND = 'next_round', 'Next Round'
        SELECT = 'select', 'Select'
        REJECT = 'reject', 'Reject'

    interview = models.OneToOneField(Interview, on_delete=models.CASCADE, related_name='feedback')

    technical_knowledge = models.PositiveSmallIntegerField()
    communication = models.PositiveSmallIntegerField()
    problem_solving = models.PositiveSmallIntegerField()
    coding = models.PositiveSmallIntegerField()
    confidence = models.PositiveSmallIntegerField()

    overall_score = models.FloatField()  # computed average, not re-entered manually
    recommendation = models.CharField(max_length=20, choices=Recommendation.choices)

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='submitted_feedback')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.interview} - {self.overall_score}/10"
