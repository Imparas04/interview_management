from rest_framework import serializers
from .models import CandidateSkill, ATSResult


class CandidateSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSkill
        fields = ['id', 'skill_name', 'source_resume', 'extracted_at']
        read_only_fields = fields


class ATSResultSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source='resume.candidate.user.username', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = ATSResult
        fields = [
            'id', 'resume', 'job', 'candidate_username', 'job_title',
            'skills_match_pct', 'experience_match_pct', 'education_match_pct',
            'projects_pct', 'certifications_pct', 'keywords_pct',
            'overall_score', 'explanation', 'calculated_at',
        ]
        read_only_fields = fields
