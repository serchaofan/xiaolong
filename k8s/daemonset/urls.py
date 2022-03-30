from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'daemonsets/', views.DaemonsetList.as_view()),
    re_path(r'daemonset/', views.DaemonsetInfo.as_view()),
] + router.urls
