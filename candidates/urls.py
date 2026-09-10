from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MyCandidateProfileView, CandidateProfileViewSet

router = DefaultRouter()
router.register('', CandidateProfileViewSet, basename='candidateprofile')

urlpatterns = [
    path('me/', MyCandidateProfileView.as_view(), name='my-candidate-profile'),
] + router.urls
