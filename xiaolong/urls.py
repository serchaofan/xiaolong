"""xiaolong URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter

import k8s.views as k8sviews

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls("文档")),
    url(r'^api-auth', include("rest_framework.urls", namespace="rest_framework")),
    # k8s
    url(r'^api/namespaces$', k8sviews.NamespaceList.as_view()),
    url(r'^api/pods$', k8sviews.PodList.as_view()),
    url(r'^api/nodes$', k8sviews.NodeList.as_view())
]
