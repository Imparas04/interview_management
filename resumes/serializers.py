from rest_framework import serializers
from .models import Resume
from .validators import validate_resume_file


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = [
            'id', 'file', 'original_filename', 'file_type',
            'parsed_text', 'parsed_name', 'parsed_email', 'parsed_phone',
            'parsing_status', 'parsing_error', 'uploaded_at',
        ]
        read_only_fields = [
            'id', 'file_type', 'parsed_text', 'parsed_name', 'parsed_email',
            'parsed_phone', 'parsing_status', 'parsing_error', 'uploaded_at',
        ]


class ResumeUploadSerializer(serializers.ModelSerializer):
    """
    Separate, minimal serializer used only for the upload action - only
    accepts a file. Everything else (original_filename, file_type, parsed
    fields) is derived server-side, never taken from the request.
    """
    class Meta:
        model = Resume
        fields = ['file']

    def validate_file(self, value):
        validate_resume_file(value)
        return value
