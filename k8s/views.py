from loguru import logger
from rest_framework.viewsets import ModelViewSet
from .serializers import ClusterModelSerializer
from rest_framework.response import Response
import rest_framework.status as status
from .models import Cluster
from loguru import logger
import json
from kubernetes import config
from kubernetes.client import Configuration, ApiClient


class ClusterModelViewSet(ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterModelSerializer

    def put(self, request, pk):
        instance = self.get_object()
        logger.info(instance)
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def get_k8s_api_client(request):
    if 'cluster' not in request.query_params.dict():
        return 400
    else:
        query_cluster = request.query_params['cluster']
        if not Cluster.objects.filter(name=query_cluster):
            return 400

    client_config = type.__call__(Configuration)

    cluster = Cluster.objects.get(name=query_cluster)
    config_json = json.loads(cluster.kubeconfig)
    config_context = config_json["current-context"]
    config.load_kube_config_from_dict(config_dict=config_json, context=config_context, persist_config=False, client_configuration=client_config)
    api_client = ApiClient(configuration=client_config)
    return api_client