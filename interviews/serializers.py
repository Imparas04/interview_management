from rest_framework import serializers
from .models import InterviewRound, Interview, InterviewFeedback
from .conflicts import has_conflict


class InterviewRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewRound
        fields = ['id', 'name', 'order']


class InterviewSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source='application.candidate.user.username', read_only=True)
    job_title = serializers.CharField(source='application.job.title', read_only=True)
    round_name = serializers.CharField(source='round.name', read_only=True)
    interviewer_username = serializers.CharField(source='interviewer.username', read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'candidate_username', 'job_title',
            'round', 'round_name', 'interviewer', 'interviewer_username',
            'scheduled_date', 'scheduled_time', 'duration_minutes',
            'location_or_link', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        interviewer = attrs.get('interviewer', getattr(self.instance, 'interviewer', None))
        scheduled_date = attrs.get('scheduled_date', getattr(self.instance, 'scheduled_date', None))
        scheduled_time = attrs.get('scheduled_time', getattr(self.instance, 'scheduled_time', None))
        duration = attrs.get('duration_minutes', getattr(self.instance, 'duration_minutes', 30))

        if attrs.get('interviewer') and attrs['interviewer'].role != attrs['interviewer'].Role.INTERVIEWER:
            raise serializers.ValidationError({"interviewer": "Selected user is not an interviewer."})

        conflict, conflicting_interview = has_conflict(
            interviewer, scheduled_date, scheduled_time, duration,
            exclude_interview_id=self.instance.id if self.instance else None,
        )
        if conflict:
            raise serializers.ValidationError(
                f"Interviewer already has an interview scheduled that overlaps this time "
                f"(existing interview #{conflicting_interview.id} on {conflicting_interview.scheduled_date} "
                f"at {conflicting_interview.scheduled_time})."
            )
        return attrs


class InterviewFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewFeedback
        fields = [
            'id', 'interview', 'technical_knowledge', 'communication',
            'problem_solving', 'coding', 'confidence',
            'overall_score', 'recommendation', 'submitted_by', 'created_at',
        ]
        read_only_fields = ['id', 'overall_score', 'submitted_by', 'created_at']

    def validate_interview(self, interview):
        if hasattr(interview, 'feedback'):
            raise serializers.ValidationError("Feedback already submitted for this interview.")
        return interview

    def create(self, validated_data):
        scores = [
            validated_data['technical_knowledge'], validated_data['communication'],
            validated_data['problem_solving'], validated_data['coding'], validated_data['confidence'],
        ]
        validated_data['overall_score'] = round(sum(scores) / len(scores), 2)
        validated_data['submitted_by'] = self.context['request'].user
        feedback = super().create(validated_data)
        feedback.interview.status = Interview.Status.COMPLETED
        feedback.interview.save(update_fields=['status'])
        return feedback
