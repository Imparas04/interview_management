from django.urls import path
from .views import (
    ApplicationListCreateView, ApplicationDetailView,
    ApplicationStatusUpdateView, CandidateRankingView,
)

urlpatterns = [
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('rank/', CandidateRankingView.as_view(), name='application-rank'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status-update'),
]
