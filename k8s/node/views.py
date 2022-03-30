from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status

from ..views import get_k8s_api_client
from kubernetes import client

class NodeList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        nodes_list = []
        nodes = api.list_node().items
        for node in nodes:
            conditions_list = []
            for condition in node.status.conditions:
                conditions_list.append(
                    dict(
                        status=condition.status,
                        type=condition.type
                    )
                )
            if 'kubernetes.io/role' not in node.metadata.labels.keys():
                role = "Unknown"
            elif 'node-role.kubernetes.io/master' in node.metadata.labels.keys() and node.metadata.labels['node-role.kubernetes.io/master'] == "":
                role = "Master"
            else:
                role = node.metadata.labels['kubernetes.io/role']
            nodes_list.append(dict(
                name=node.metadata.name,
                labels=node.metadata.labels,
                creationTimestamp=datetime.strftime(node.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                role=role,
                status=conditions_list[-1]['type'] if conditions_list[-1]['status'] == 'True' else 'NotReady',
                kubelet_version=node.status.node_info.kubelet_version,
                unschedulable=node.spec.unschedulable,
            ))

        return Response(data={'data': nodes_list}, status=status.HTTP_200_OK)

class NodeInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        name = request.query_params['name']
        node = api.read_node(name=name)

        conditions_list = []
        for condition in node.status.conditions:
            conditions_list.append(
                dict(
                    last_heartbeat_time=condition.last_heartbeat_time,
                    last_transition_time=condition.last_transition_time,
                    message=condition.message,
                    reason=condition.reason,
                    status=condition.status,
                    type=condition.type
                )
            )
        images_list = []
        if node.status.images:
            for image in node.status.images:
                images_list.append(
                    dict(
                        names=image.names[-1],
                        size_bytes=round(image.size_bytes/1000/1000, 1)
                    )
                )
        else:
            images_list = []
        addresses_list = []
        for address in node.status.addresses:
            addresses_list.append(
                dict(
                    address=address.address,
                    type=address.type
                )
            )
        taints_list = []
        if node.spec.taints:
            for taint in node.spec.taints:
                taints_list.append(
                    dict(
                        effect=taint.effect,
                        key=taint.key,
                        time_added=taint.time_added,
                        value=taint.value
                    )
                )
        else:
            taints_list = []
        node = dict(
            name=node.metadata.name,
            podCidr=node.spec.pod_cidr,
            capacity=node.status.capacity,
            allocatable=node.status.allocatable,
            labels=node.metadata.labels,
            annotations=node.metadata.annotations,
            creationTimestamp=datetime.strftime(node.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            nodeInfo=dict(
                architecture=node.status.node_info.architecture,
                boot_id=node.status.node_info.boot_id,
                container_runtime_version=node.status.node_info.container_runtime_version,
                kernel_version=node.status.node_info.kernel_version,
                kubelet_version=node.status.node_info.kubelet_version,
                machine_id=node.status.node_info.machine_id,
                operating_system=node.status.node_info.operating_system,
                os_image=node.status.node_info.os_image,
                system_uuid=node.status.node_info.system_uuid
            ),
            # role=node.metadata.labels['kubernetes.io/role'],
            kubelet_version=node.status.node_info.kubelet_version,
            conditions=conditions_list,
            status=conditions_list[-1]['type'] if conditions_list[-1]['status'] == 'True' else 'NotReady',
            images=images_list,
            addresses=addresses_list,
            taints=taints_list,
            unschedulable=node.spec.unschedulable,
            daemonEndpoints=dict(
                kubelet_endpoint=dict(port=node.status.daemon_endpoints.kubelet_endpoint.port),
            )
        )

        return Response(data={'data': node}, status=status.HTTP_200_OK)

class NamespaceList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        namespaces_list = []
        namespaces = api.list_namespace().items
        for namespace in namespaces:
            namespaces_list.append(
                dict(
                    name=namespace.metadata.name,
                    creationTimestamp=datetime.strftime(namespace.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    status=namespace.status.phase
                )
            )

        return Response(data={'data': namespaces_list}, status=status.HTTP_200_OK)
