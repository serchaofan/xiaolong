from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class NetworkPolicyList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.NetworkingV1Api(api_client=api_client)
        networkpolicies_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            networkpolicies = api.list_network_policy_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            networkpolicies = api.list_namespaced_network_policy(namespace=query_ns).items
        logger.info(f"Getting networkpolicies Total: {len(networkpolicies)} networkpolicies")
        for networkpolicy in networkpolicies:
            networkpolicies_list.append(
                dict(
                    name=networkpolicy.metadata.name,
                    namespace=networkpolicy.metadata.namespace,
                    labels=networkpolicy.metadata.labels,
                    creationTimestamp=datetime.strftime(networkpolicy.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )

        return Response(data={'data': networkpolicies_list}, status=status.HTTP_200_OK)
