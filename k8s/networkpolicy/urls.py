from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'networkpolicies/', views.NetworkPolicyList.as_view()),
] + router.urls
