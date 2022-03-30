from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class ConfigMapList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        configmaps_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            configmaps = api.list_config_map_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            configmaps = api.list_namespaced_config_map(namespace=query_ns).items
        logger.info(f"Getting configmaps Total: {len(configmaps)} configmaps")
        for configmap in configmaps:
            configmaps_list.append(
                dict(
                    name=configmap.metadata.name,
                    namespace=configmap.metadata.namespace,
                    labels=configmap.metadata.labels,
                    creationTimestamp=datetime.strftime(configmap.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )

        return Response(data={'data': configmaps_list}, status=status.HTTP_200_OK)


class SecretList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        secrets_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            secrets = api.list_secret_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            secrets = api.list_namespaced_secret(namespace=query_ns).items
        logger.info(f"Getting secrets Total: {len(secrets)} secrets")
        for secret in secrets:
            secrets_list.append(
                dict(
                    name=secret.metadata.name,
                    namespace=secret.metadata.namespace,
                    labels=secret.metadata.labels,
                    creationTimestamp=datetime.strftime(secret.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    type=secret.type
                )
            )

        return Response(data={'data': secrets_list}, status=status.HTTP_200_OK)


class SecretInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        name = request.query_params['name']
        namespace = request.query_params['namespace']
        secret = api.read_namespaced_secret(name=name, namespace=namespace)
        secret = dict(
            name=secret.metadata.name,
            namespace=secret.metadata.namespace,
            labels=secret.metadata.labels,
            creationTimestamp=datetime.strftime(secret.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            type=secret.type,
            data=secret.data
        )

        return Response(data={'data': secret}, status=status.HTTP_200_OK)
