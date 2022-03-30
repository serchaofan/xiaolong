from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'statefulsets/', views.StatefulsetList.as_view()),
    re_path(r'statefulset/', views.StatefulsetInfo.as_view()),
] + router.urls
