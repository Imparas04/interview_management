from rest_framework import serializers
from .models import CandidateProfile
from accounts.serializers import UserSerializer


class CandidateProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    recommended_department_name = serializers.CharField(
        source='recommended_department.name', read_only=True, default=None
    )

    class Meta:
        model = CandidateProfile
        fields = [
            'id', 'user', 'phone', 'address', 'date_of_birth', 'summary',
            'linkedin_url', 'portfolio_url',
            'recommended_department', 'recommended_department_name',
            'created_at', 'updated_at',
        ]
        # recommended_department is set by the ATS engine later, not by the
        # candidate themself - candidates can never assign their own
        # recommended department through this API.
        read_only_fields = ['id', 'user', 'recommended_department', 'created_at', 'updated_at']
