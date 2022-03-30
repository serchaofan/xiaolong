from django.contrib import admin
from django.urls import re_path, include
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^api/', include("k8s.urls")),
]
