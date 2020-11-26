from rest_framework.response import Response

from kubernetes import config, client
from rest_framework.views import APIView
from loguru import logger
import json
from django.http import JsonResponse


class NodeList(APIView):
    def get(self, request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        nodes_list = []
        nodes = api.list_node().items
        for node in nodes:
            logger.info(f"capacity: {node.metadata.name}")
            # nodes_list.append(dict(
            #     name=node.metadata.name,
            #     podCidr=node.spec.pod_cidr,
            #     capacity=node.status.capacity,
            #     allocatable=node.status.allocatable,
            #     nodeInfo=node.status.node_info,
            #     daemonEndpoints=node.status.daemon_endpoints
            # ))
        logger.debug(f"{nodes_list}")
        data = {
            'code': 20000,
            'data': nodes_list
        }
        return Response(data=data)


class NamespaceList(APIView):
    def get(self, request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        namespaces_list = []
        namespaces = api.list_namespace().items
        for namespace in namespaces:
            namespaces_list.append(
                dict(
                    name=namespace.metadata.name,
                    creationTimestamp=namespace.metadata.creation_timestamp,
                    status=namespace.status.phase
                )
            )
        data = {
            'code': 20000,
            'data': namespaces_list
        }
        return Response(data=data)


class PodList(APIView):
    def get(self, request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        pods_list = []
        logger.info(f"{request} {request.query_params}")
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All pods")
            pods = api.list_pod_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            pods = api.list_namespaced_pod(namespace=query_ns).items
        logger.info(f"Getting pods Total: {len(pods)} Pods")
        for pod in pods:
            pods_list.append(
                dict(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    labels=pod.metadata.labels,
                    creationTimestamp=pod.metadata.creation_timestamp,
                    hostname=pod.spec.hostname,
                    nodename=pod.spec.node_name,
                    dnsPolicy=pod.spec.dns_policy,
                    restartPolicy=pod.spec.restart_policy,
                    # serviceAccount=pod.spec.serviceAccount,
                    # volumes=json.pod.spec.volumes,
                    hostIP=pod.status.host_ip,
                    podIP=pod.status.pod_ip,
                    startTime=pod.status.start_time
                )
            )
        data = {
            'code': 20000,
            'data': pods_list
        }
        return Response(data=data)


class DeploymentList(APIView):
    def get(self, request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
