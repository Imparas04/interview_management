from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume
from jobs.models import JobRole
from .models import CandidateSkill, ATSResult
from .serializers import CandidateSkillSerializer, ATSResultSerializer
from .skill_extraction import extract_skills
from .scoring import calculate_ats_score
from .department_recommendation import recommend_department


def _can_access_resume(user, resume):
    if user.role == user.Role.CANDIDATE:
        return resume.candidate.user_id == user.id
    return user.role in [user.Role.ADMIN, user.Role.HR, user.Role.INTERVIEWER]


class ExtractSkillsView(APIView):
    """
    POST /api/ats/resumes/{resume_id}/extract-skills/

    Runs the rule-based extraction on a resume's already-parsed text and
    stores the result. Replaces the candidate's existing CandidateSkill
    rows with the fresh extraction, so their profile always reflects their
    MOST RECENT resume rather than accumulating skills from every resume
    they've ever uploaded.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, resume_id):
        resume = get_object_or_404(Resume, id=resume_id)

        if not _can_access_resume(request.user, resume):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if resume.parsing_status != Resume.ParsingStatus.SUCCESS:
            return Response(
                {"detail": "Resume text was not parsed successfully; cannot extract skills."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        skill_names = extract_skills(resume.parsed_text)

        candidate = resume.candidate
        candidate.skills.all().delete()
        CandidateSkill.objects.bulk_create([
            CandidateSkill(candidate=candidate, skill_name=name, source_resume=resume)
            for name in skill_names
        ])

        return Response({
            "resume_id": resume.id,
            "extracted_skills": skill_names,
            "count": len(skill_names),
        }, status=status.HTTP_200_OK)


class CandidateSkillListView(generics.ListAPIView):
    """
    GET /api/ats/candidates/{candidate_id}/skills/
    Candidate: only their own (candidate_id must match their profile).
    HR/Admin/Interviewer: any candidate's current extracted skills.
    """
    serializer_class = CandidateSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        candidate_id = self.kwargs['candidate_id']
        user = self.request.user
        if user.role == user.Role.CANDIDATE:
            from candidates.models import CandidateProfile
            profile, _ = CandidateProfile.objects.get_or_create(user=user)
            if str(profile.id) != str(candidate_id):
                return CandidateSkill.objects.none()
        return CandidateSkill.objects.filter(candidate_id=candidate_id)


class CalculateATSScoreView(APIView):
    """
    POST /api/ats/score/   body: {"resume_id": 1, "job_id": 2}

    Runs the full weighted ATS calculation and stores/updates the result.
    Requires skills to have already been extracted for this resume
    (Phase 7) - we don't silently re-extract here, so the score is always
    calculated against a skill set the candidate/HR has explicitly seen.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get('resume_id')
        job_id = request.data.get('job_id')
        if not resume_id or not job_id:
            return Response({"detail": "resume_id and job_id are required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id)
        job = get_object_or_404(JobRole, id=job_id)

        if not _can_access_resume(request.user, resume):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if resume.parsing_status != Resume.ParsingStatus.SUCCESS:
            return Response({"detail": "Resume must be successfully parsed before scoring."}, status=status.HTTP_400_BAD_REQUEST)

        candidate_skill_names = list(resume.candidate.skills.values_list('skill_name', flat=True))
        if not candidate_skill_names:
            return Response(
                {"detail": "No extracted skills found for this candidate. Run skill extraction first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        score_data = calculate_ats_score(resume, job, candidate_skill_names)

        result, _created = ATSResult.objects.update_or_create(
            resume=resume, job=job, defaults=score_data
        )

        return Response(ATSResultSerializer(result).data, status=status.HTTP_200_OK)


class ATSResultDetailView(generics.RetrieveAPIView):
    """GET /api/ats/results/{id}/ - view one stored ATS result."""
    queryset = ATSResult.objects.select_related('resume__candidate__user', 'job')
    serializer_class = ATSResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if not _can_access_resume(self.request.user, obj.resume):
            self.permission_denied(self.request, message="Not allowed.")
        return obj


class ATSResultListView(generics.ListAPIView):
    """
    GET /api/ats/results/?job=<id>            HR/Admin - all candidates scored for a job
    GET /api/ats/results/?resume=<id>         owner or HR/Admin/Interviewer
    Used by Phase 11's candidate ranking as the underlying data source.
    """
    serializer_class = ATSResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = ATSResult.objects.select_related('resume__candidate__user', 'job')

        if user.role == user.Role.CANDIDATE:
            qs = qs.filter(resume__candidate__user=user)

        job_id = self.request.query_params.get('job')
        resume_id = self.request.query_params.get('resume')
        if job_id:
            qs = qs.filter(job_id=job_id)
        if resume_id:
            qs = qs.filter(resume_id=resume_id)
        return qs


class RecommendDepartmentView(APIView):
    """
    POST /api/ats/candidates/{candidate_id}/recommend-department/

    Uses the candidate's currently extracted skills (Phase 7) to pick the
    best-matching department from ats/department_data.py and saves the
    result onto CandidateProfile. Candidate can trigger this for
    themselves; HR/Admin can trigger it for any candidate.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, candidate_id):
        from candidates.models import CandidateProfile
        candidate = get_object_or_404(CandidateProfile, id=candidate_id)

        user = request.user
        if user.role == user.Role.CANDIDATE and candidate.user_id != user.id:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        if user.role == user.Role.INTERVIEWER:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        skill_names = list(candidate.skills.values_list('skill_name', flat=True))
        if not skill_names:
            return Response(
                {"detail": "No extracted skills found for this candidate. Run skill extraction first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dept_name, confidence, explanation = recommend_department(skill_names)

        from departments.models import Department
        department_obj = Department.objects.filter(name=dept_name).first() if dept_name else None

        candidate.recommended_department = department_obj
        candidate.recommended_department_confidence = confidence
        candidate.recommended_department_explanation = explanation
        candidate.save()

        return Response({
            "candidate_id": candidate.id,
            "recommended_department": dept_name,
            "confidence": confidence,
            "explanation": explanation,
        }, status=status.HTTP_200_OK)
