from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'sas/', views.ServiceAccountList.as_view()),
    re_path(r'roles/', views.RoleList.as_view()),
    re_path(r'role/', views.RoleInfo.as_view()),
    re_path(r'rolebindings/', views.RoleBindingList.as_view()),
    re_path(r'rolebinding/', views.RoleBindingInfo.as_view()),
    re_path(r'clusterroles/', views.ClusterRoleList.as_view()),
    re_path(r'clusterrole/', views.ClusterRoleInfo.as_view()),
    re_path(r'clusterrolebindings/', views.ClusterRoleBindingList.as_view()),
    re_path(r'clusterrolebinding/', views.ClusterRoleBindingInfo.as_view()),
] + router.urls
