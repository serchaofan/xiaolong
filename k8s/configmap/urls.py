from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'configmaps/', views.ConfigMapList.as_view()),
    re_path(r'secrets/', views.SecretList.as_view()),
    re_path(r'secret/', views.SecretInfo.as_view()),
] + router.urls
