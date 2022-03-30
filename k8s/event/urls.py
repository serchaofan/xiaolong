from django.urls import re_path
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()

urlpatterns = [
    re_path(r'events/', views.EventList.as_view()),
    re_path(r'event/', views.EventInfo.as_view()),
] + router.urls
