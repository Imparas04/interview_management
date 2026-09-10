from rest_framework import serializers
from .models import JobRole, JobSkill
from departments.models import Department


class JobSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobSkill
        fields = ['id', 'skill_name', 'weight']


class JobRoleSerializer(serializers.ModelSerializer):
    """
    required_skills is nested and writable: the frontend sends skills as
    a list of {"skill_name": "...", "weight": 2} objects inside the same
    request that creates/updates the job, instead of needing a second
    round-trip of API calls per skill.
    """
    required_skills = JobSkillSerializer(many=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = JobRole
        fields = [
            'id', 'title', 'department', 'department_name', 'description',
            'experience_min', 'experience_max', 'education_required', 'keywords',
            'num_openings', 'location', 'job_type', 'status',
            'application_deadline', 'required_skills',
            'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_department(self, value):
        if not Department.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Selected department is not active.")
        return value

    def create(self, validated_data):
        skills_data = validated_data.pop('required_skills')
        request = self.context.get('request')
        job = JobRole.objects.create(created_by=request.user if request else None, **validated_data)
        for skill in skills_data:
            JobSkill.objects.create(job_role=job, **skill)
        return job

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('required_skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if skills_data is not None:
            # Replace the whole skills set on update - simplest correct
            # behaviour for "edit job" from the frontend's point of view.
            instance.required_skills.all().delete()
            for skill in skills_data:
                JobSkill.objects.create(job_role=instance, **skill)

        return instance
