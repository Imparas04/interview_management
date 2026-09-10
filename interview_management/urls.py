from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Phase 2 onward: path('api/auth/', include('accounts.urls')), etc.
]
