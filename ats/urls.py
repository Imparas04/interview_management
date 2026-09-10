from django.urls import path
from .views import ExtractSkillsView, CandidateSkillListView

urlpatterns = [
    path('resumes/<int:resume_id>/extract-skills/', ExtractSkillsView.as_view(), name='extract-skills'),
    path('candidates/<int:candidate_id>/skills/', CandidateSkillListView.as_view(), name='candidate-skills'),
]
