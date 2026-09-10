from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source='candidate.user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    department_name = serializers.CharField(source='job.department.name', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'candidate', 'candidate_username', 'job', 'job_title',
            'department_name', 'resume', 'status', 'applied_at', 'updated_at',
        ]
        read_only_fields = ['id', 'candidate', 'status', 'applied_at', 'updated_at']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Used only for POST (a candidate applying). candidate is set from
    request.user in the view - never accepted from the request body, so
    nobody can apply on another candidate's behalf.
    """
    class Meta:
        model = Application
        fields = ['job', 'resume']

    def validate(self, attrs):
        resume = attrs['resume']
        request = self.context['request']
        if resume.candidate.user_id != request.user.id:
            raise serializers.ValidationError("You can only apply using your own resume.")
        return attrs


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.Status.choices)
