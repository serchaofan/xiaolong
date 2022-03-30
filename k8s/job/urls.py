from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'cronjobs/', views.CronjobList.as_view()),
    re_path(r'jobs/', views.JobList.as_view()),
] + router.urls
