from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'nodes/', views.NodeList.as_view()),
    re_path(r'node/', views.NodeInfo.as_view()),
    re_path(r'namespace/', views.NamespaceList.as_view())
] + router.urls
