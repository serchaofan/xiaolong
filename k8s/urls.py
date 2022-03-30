from rest_framework.routers import DefaultRouter
from .node.urls import urlpatterns as node_urlpatterns
from .pod.urls import urlpatterns as pod_urlpatterns
from .deployment.url import urlpatterns as deployment_urlpatterns
from .daemonset.urls import urlpatterns as daemonset_urlpatterns
from .replicaset.urls import urlpatterns as replicaset_urlpatterns

from .views import ClusterModelViewSet

router = DefaultRouter()
router.register("cluster", ClusterModelViewSet, basename="cluster")

urlpatterns = [

] + node_urlpatterns + \
    pod_urlpatterns + \
    deployment_urlpatterns + \
    daemonset_urlpatterns + \
    replicaset_urlpatterns + \
    router.urls
