from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Used ONLY for candidate self-registration.
    Role is never accepted from the request - it's hardcoded to CANDIDATE
    so nobody can register themselves as HR/Admin/Interviewer via this endpoint.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=User.Role.CANDIDATE,  # hardcoded, not from client input
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Safe, read-only representation of a user."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']
