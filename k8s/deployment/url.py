from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'deployments/', views.DeploymentList.as_view()),
    re_path(r'deployment/', views.DeploymentInfo.as_view()),
] + router.urls
