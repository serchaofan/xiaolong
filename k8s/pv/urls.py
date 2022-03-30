from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'pvcs/', views.PVCList.as_view()),
    re_path(r'pvs/', views.PVList.as_view()),
] + router.urls
