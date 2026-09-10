from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MyCandidateProfileView, CandidateProfileViewSet, CandidateSearchView

router = DefaultRouter()
router.register('', CandidateProfileViewSet, basename='candidateprofile')

urlpatterns = [
    path('me/', MyCandidateProfileView.as_view(), name='my-candidate-profile'),
    path('search/', CandidateSearchView.as_view(), name='candidate-search'),
] + router.urls
