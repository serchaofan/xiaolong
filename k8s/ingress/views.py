from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class IngressList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.NetworkingV1beta1Api(api_client=api_client)
        ingresses_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            ingresses = api.list_ingress_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            ingresses = api.list_namespaced_ingress(namespace=query_ns).items
        logger.info(f"Getting ingresses Total: {len(ingresses)} ingresses")
        for ingress in ingresses:
            ingresses_list.append(
                dict(
                    name=ingress.metadata.name,
                    namespace=ingress.metadata.namespace,
                    labels=ingress.metadata.labels,
                    creationTimestamp=datetime.strftime(ingress.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )

        return Response(data={'data': ingresses_list}, status=status.HTTP_200_OK)
