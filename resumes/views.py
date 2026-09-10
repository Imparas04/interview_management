import os
from django.http import FileResponse, Http404
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Resume
from .serializers import ResumeSerializer, ResumeUploadSerializer
from .services import parse_resume_file
from accounts.permissions import IsCandidate
from candidates.models import CandidateProfile


class ResumeUploadView(generics.CreateAPIView):
    """
    POST /api/resumes/upload/  - candidate only.
    Saves the file, then immediately runs parsing synchronously and stores
    the result. If parsing fails (e.g. scanned/image PDF with no text
    layer), the Resume row is still kept with parsing_status=FAILED so the
    candidate/HR can see what happened instead of the upload silently
    vanishing.
    """
    permission_classes = [permissions.IsAuthenticated, IsCandidate]
    serializer_class = ResumeUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data['file']
        original_filename = uploaded_file.name
        file_type = original_filename.rsplit('.', 1)[-1].lower()

        candidate_profile, _ = CandidateProfile.objects.get_or_create(user=request.user)

        resume = Resume.objects.create(
            candidate=candidate_profile,
            file=uploaded_file,
            original_filename=original_filename,
            file_type=file_type,
        )

        try:
            parsed = parse_resume_file(resume.file.path, file_type)
            resume.parsed_text = parsed['parsed_text']
            resume.parsed_name = parsed['parsed_name']
            resume.parsed_email = parsed['parsed_email']
            resume.parsed_phone = parsed['parsed_phone']
            resume.parsing_status = Resume.ParsingStatus.SUCCESS
        except Exception as exc:
            resume.parsing_status = Resume.ParsingStatus.FAILED
            resume.parsing_error = str(exc)

        resume.save()

        return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)


class ResumeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/resumes/           candidate: only their own; HR/Admin/Interviewer: all
    GET /api/resumes/{id}/      same rule, enforced in get_queryset

    Read-only - resumes are never edited through the API, only re-uploaded
    (creating a new Resume row) or deleted.
    """
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Resume.objects.select_related('candidate__user')
        if user.role == user.Role.CANDIDATE:
            return qs.filter(candidate__user=user)
        return qs  # HR, Admin, Interviewer can see all


class ResumeDownloadView(APIView):
    """
    GET /api/resumes/{id}/download/
    Streams the actual file. This exists as its own endpoint (instead of
    just exposing the raw media URL) so we can enforce the same permission
    check as ResumeViewSet before ever touching the filesystem - resumes
    must never be servable by guessing a media URL.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        try:
            resume = Resume.objects.select_related('candidate__user').get(pk=pk)
        except Resume.DoesNotExist:
            raise Http404

        if user.role == user.Role.CANDIDATE and resume.candidate.user_id != user.id:
            raise Http404  # 404, not 403 - don't reveal that another candidate's resume exists

        if not resume.file or not os.path.exists(resume.file.path):
            raise Http404

        return FileResponse(
            open(resume.file.path, 'rb'),
            as_attachment=True,
            filename=resume.original_filename,
        )
