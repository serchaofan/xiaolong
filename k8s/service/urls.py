from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'services/', views.ServiceList.as_view()),
    re_path(r'service/', views.ServiceInfo.as_view()),
] + router.urls
