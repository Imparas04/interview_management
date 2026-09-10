from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    InterviewRoundViewSet, InterviewListCreateView, InterviewDetailView,
    InterviewFeedbackCreateView, InterviewFeedbackListView,
)

router = DefaultRouter()
router.register('rounds', InterviewRoundViewSet, basename='interview-round')

urlpatterns = [
    path('', InterviewListCreateView.as_view(), name='interview-list-create'),
    path('<int:pk>/', InterviewDetailView.as_view(), name='interview-detail'),
    path('feedback/', InterviewFeedbackCreateView.as_view(), name='interview-feedback-create'),
    path('feedback/list/', InterviewFeedbackListView.as_view(), name='interview-feedback-list'),
] + router.urls
