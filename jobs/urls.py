from rest_framework.routers import DefaultRouter
from .views import JobRoleViewSet

router = DefaultRouter()
router.register('', JobRoleViewSet, basename='jobrole')

urlpatterns = router.urls
