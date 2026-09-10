from django.urls import path
from .views import DashboardOverviewView, CandidateDashboardSummaryView

urlpatterns = [
    path('overview/', DashboardOverviewView.as_view(), name='analytics-overview'),
    path('candidate-summary/', CandidateDashboardSummaryView.as_view(), name='analytics-candidate-summary'),
]
