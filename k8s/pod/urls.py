from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'pods/', views.PodList.as_view()),
    re_path(r'pod/', views.PodInfo.as_view()),
] + router.urls
