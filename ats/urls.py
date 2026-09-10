from django.urls import path
from .views import (
    ExtractSkillsView, CandidateSkillListView,
    CalculateATSScoreView, ATSResultDetailView, ATSResultListView,
    RecommendDepartmentView,
)

urlpatterns = [
    path('resumes/<int:resume_id>/extract-skills/', ExtractSkillsView.as_view(), name='extract-skills'),
    path('candidates/<int:candidate_id>/skills/', CandidateSkillListView.as_view(), name='candidate-skills'),
    path('score/', CalculateATSScoreView.as_view(), name='ats-score'),
    path('results/<int:pk>/', ATSResultDetailView.as_view(), name='ats-result-detail'),
    path('results/', ATSResultListView.as_view(), name='ats-result-list'),
    path('candidates/<int:candidate_id>/recommend-department/', RecommendDepartmentView.as_view(), name='recommend-department'),
]
