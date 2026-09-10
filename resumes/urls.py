from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ResumeUploadView, ResumeViewSet, ResumeDownloadView

router = DefaultRouter()
router.register('', ResumeViewSet, basename='resume')

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('<int:pk>/download/', ResumeDownloadView.as_view(), name='resume-download'),
] + router.urls
