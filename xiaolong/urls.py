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
    # list
    url(r'^api/namespaces$', k8s_views.NamespaceList.as_view()),
    url(r'^api/pods$', k8s_views.PodList.as_view()),
    url(r'^api/nodes$', k8s_views.NodeList.as_view()),
    url(r'^api/deployments$', k8s_views.DeploymentList.as_view()),
    url(r'^api/daemonsets$', k8s_views.DaemonsetList.as_view()),
    url(r'^api/replicasets$', k8s_views.ReplicasetList.as_view()),
    url(r'^api/statefulsets$', k8s_views.StatefulsetList.as_view()),
    url(r'^api/services$', k8s_views.ServiceList.as_view()),
    url(r'^api/ingresses$', k8s_views.IngressList.as_view()),
    url(r'^api/network_policies$', k8s_views.NetworkPolicyList.as_view()),
    url(r'^api/cronjobs$', k8s_views.CronjobList.as_view()),
    url(r'^api/jobs$', k8s_views.JobList.as_view()),
    url(r'^api/pvs$', k8s_views.PVList.as_view()),
    url(r'^api/pvcs$', k8s_views.PVCList.as_view()),
    url(r'^api/configmaps$', k8s_views.ConfigMapList.as_view()),
    url(r'^api/secrets$', k8s_views.SecretList.as_view()),
    url(r'^api/roles$', k8s_views.RoleList.as_view()),
    url(r'^api/role_bindings$', k8s_views.RoleBindingList.as_view()),
    url(r'^api/cluster_roles$', k8s_views.ClusterRoleList.as_view()),
    url(r'^api/cluster_role_bindings$', k8s_views.ClusterRoleBindingList.as_view()),
    url(r'^api/events$', k8s_views.EventList.as_view()),
    # info
    url(r'^api/node', k8s_views.NodeInfo.as_view()),
    url(r'^api/pod', k8s_views.PodInfo.as_view()),
    url(r'^api/secret', k8s_views.SecretInfo.as_view()),
    url(r'^api/role_binding', k8s_views.RoleBindingInfo.as_view()),
    url(r'^api/role', k8s_views.RoleInfo.as_view()),
    url(r'^api/cluster_role_binding', k8s_views.ClusterRoleBindingInfo.as_view()),
    url(r'^api/cluster_role', k8s_views.ClusterRoleInfo.as_view()),
    url(r'^api/event', k8s_views.EventInfo.as_view()),


]

