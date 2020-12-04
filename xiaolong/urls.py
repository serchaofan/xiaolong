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

import k8s.views as k8s_views

router = DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls("文档")),
    url(r'^api-auth', include("rest_framework.urls", namespace="rest_framework")),
    # k8s
    url(r'^api/namespaces$', k8s_views.NamespaceList.as_view()),
    url(r'^api/pods$', k8s_views.PodList.as_view()),
    url(r'^api/nodes$', k8s_views.NodeList.as_view()),
    url(r'^api/deployments$', k8s_views.DeploymentList.as_view()),
    url(r'^api/daemonsets$', k8s_views.DaemonsetList.as_view()),
    url(r'^api/replicasets$', k8s_views.ReplicasetList.as_view()),
    url(r'^api/statefulsets$', k8s_views.StatefulsetList.as_view()),
    url(r'^api/services$', k8s_views.ServiceList.as_view()),

    url(r'^api/node', k8s_views.NodeInfo.as_view()),
    url(r'^api/pod', k8s_views.PodInfo.as_view()),


]
