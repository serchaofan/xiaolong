from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'replicasets/', views.ReplicasetList.as_view()),
    re_path(r'replicaset/', views.ReplicasetInfo.as_view()),
] + router.urls
