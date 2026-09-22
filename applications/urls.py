from django.urls import path
from .views import (
    ApplicationListCreateView, ApplicationDetailView,
    ApplicationStatusUpdateView, CandidateRankingView, AutoProcessApplicationsView,
)

urlpatterns = [
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('rank/', CandidateRankingView.as_view(), name='application-rank'),
    path('auto-process/', AutoProcessApplicationsView.as_view(), name='application-auto-process'),
    path('<int:pk>/', ApplicationDetailView.as_view(), name='application-detail'),
    path('<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status-update'),
]
