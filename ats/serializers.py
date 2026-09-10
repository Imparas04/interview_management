from rest_framework import serializers
from .models import CandidateSkill


class CandidateSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSkill
        fields = ['id', 'skill_name', 'source_resume', 'extracted_at']
        read_only_fields = fields
