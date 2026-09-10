from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from resumes.models import Resume
from .models import CandidateSkill
from .serializers import CandidateSkillSerializer
from .skill_extraction import extract_skills


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
