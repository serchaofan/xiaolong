from operator import imod
from rest_framework.routers import DefaultRouter
from .node.urls import urlpatterns as node_urlpatterns
from .pod.urls import urlpatterns as pod_urlpatterns
from .deployment.url import urlpatterns as deployment_urlpatterns
from .daemonset.urls import urlpatterns as daemonset_urlpatterns
from .replicaset.urls import urlpatterns as replicaset_urlpatterns
from .statefulset.urls import urlpatterns as statefulset_urlpatterns
from .service.urls import urlpatterns as service_urlpatterns
from .ingress.urls import urlpatterns as ingress_urlpatterns
from .networkpolicy.urls import urlpatterns as networkpolicy_urlpatterns
from .job.urls import urlpatterns as job_urlpatterns
from .configmap.urls import urlpatterns as configmap_urlpatterns
from .pv.urls import urlpatterns as pv_urlpatterns
from .role.urls import urlpatterns as role_urlpatterns
from .event.urls import urlpatterns as event_urlpatterns

from .views import ClusterModelViewSet

router = DefaultRouter()
router.register("cluster", ClusterModelViewSet, basename="cluster")

urlpatterns = [
] + node_urlpatterns + \
    pod_urlpatterns + \
    deployment_urlpatterns + \
    daemonset_urlpatterns + \
    replicaset_urlpatterns + \
    statefulset_urlpatterns + \
    service_urlpatterns + \
    ingress_urlpatterns + \
    networkpolicy_urlpatterns + \
    job_urlpatterns + \
    configmap_urlpatterns + \
    pv_urlpatterns + \
    role_urlpatterns + \
    event_urlpatterns + \
    router.urls
