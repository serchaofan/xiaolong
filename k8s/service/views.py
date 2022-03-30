from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class ServiceList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        services_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            services = api.list_service_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            services = api.list_namespaced_service(namespace=query_ns).items
        logger.info(f"Getting services Total: {len(services)} services")
        for service in services:
            services_list.append(
                dict(
                    name=service.metadata.name,
                    namespace=service.metadata.namespace,
                    labels=service.metadata.labels,
                    creationTimestamp=datetime.strftime(service.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    clusterIP=service.spec.cluster_ip,
                    externalTrafficPolicy=service.spec.external_traffic_policy,
                    ports=[
                        dict(
                            name=port.name,
                            node_port=port.node_port,
                            port=port.port,
                            protocol=port.protocol,
                            target_port=port.target_port
                        ) for port in service.spec.ports
                    ],
                    selector=service.spec.selector,
                    type=service.spec.type,
                    status=dict(
                        load_balancer=dict(
                            ingress=service.status.load_balancer.ingress
                        )
                    )
                )
            )

        return Response(data={'data': services_list}, status=status.HTTP_200_OK)


class ServiceInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        if 'name' not in request.query_params.dict() or 'namespace' not in request.query_params.dict():
            return Response({"data": "Name Or Namespace Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.query_params['name']
        namespace = request.query_params['namespace']
        service = api.read_namespaced_service(name=name, namespace=namespace)
        service = dict(
            name=service.metadata.name,
            namespace=service.metadata.namespace,
            labels=service.metadata.labels,
            creationTimestamp=datetime.strftime(service.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            clusterIP=service.spec.cluster_ip,
            externalTrafficPolicy=service.spec.external_traffic_policy,
            ports=[
                dict(
                    name=port.name,
                    node_port=port.node_port,
                    port=port.port,
                    protocol=port.protocol,
                    target_port=port.target_port
                ) for port in service.spec.ports
            ],
            selector=service.spec.selector,
            type=service.spec.type,
            status=dict(
                load_balancer=dict(
                    ingress=service.status.load_balancer.ingress
                )
            )
        )

        return Response(data={'data': service}, status=status.HTTP_200_OK)
