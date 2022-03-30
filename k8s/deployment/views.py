from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client

class DeploymentList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.AppsV1Api(api_client=api_client)
        deployments_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All deployments")
            deployments = api.list_deployment_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            deployments = api.list_namespaced_deployment(namespace=query_ns).items
        logger.info(f"Getting deployments Total: {len(deployments)} deployments")
        for deployment in deployments:
            conditions_list = []
            for condition in deployment.status.conditions:
                conditions_list.append(
                    dict(
                        last_transition_time=condition.last_transition_time,
                        last_update_time=condition.last_update_time,
                        message=condition.message,
                        reason=condition.reason,
                        status=condition.status,
                        type=condition.type
                    )
                )
            deployments_list.append(
                dict(
                    name=deployment.metadata.name,
                    namespace=deployment.metadata.namespace,
                    labels=deployment.metadata.labels,
                    creationTimestamp=datetime.strftime(deployment.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    # status=dict(
                    #     available_replicas=deployment.status.available_replicas,
                    #     conditions=conditions_list,
                    #     ready_replicas=deployment.status.ready_replicas,
                    #     replicas=deployment.status.replicas,
                    #     unavailable_replicas=deployment.status.unavailable_replicas,
                    #     updated_replicas=deployment.status.updated_replicas
                    # )
                    status=f"{deployment.status.ready_replicas}/{deployment.status.replicas}"
                )
            )

        return Response(data={'data': deployments_list}, status=status.HTTP_200_OK)


class DeploymentInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.AppsV1Api(api_client=api_client)
        if 'name' not in request.query_params.dict() or 'namespace' not in request.query_params.dict():
            return Response({"data": "Name Or Namespace Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)

        name = request.query_params['name']
        namespace = request.query_params['namespace']
        deployment = api.read_namespaced_deployment(name=name, namespace=namespace)
        containers_list = []
        for container in deployment.spec.template.spec.containers:
            envs_list = []
            if container.env:
                for env in container.env:
                    envs_list.append(
                        dict(
                            name=env.name,
                            value=env.value
                        )
                    )
            else:
                envs_list = []
            ports_list = []
            if container.ports:
                for port in container.ports:
                    ports_list.append(
                        dict(
                            container_port=port.container_port,
                            protocol=port.protocol
                        )
                    )
            else:
                ports_list = []
            volume_mounts_list = []
            if container.volume_mounts:
                for mount in container.volume_mounts:
                    volume_mounts_list.append(
                        dict(
                            mount_path=mount.mount_path,
                            name=mount.name
                        )
                    )
            else:
                volume_mounts_list = []

            containers_list.append(
                dict(
                    name=container.name,
                    image=container.image,
                    env=envs_list,
                    image_pull_policy=container.image_pull_policy,
                    # liveness_probe=dict(
                    #     container.liveness_probe
                    # ),
                    resources=dict(
                        limits=container.resources.limits,
                        requests=container.resources.requests
                    ),
                    volume_mounts=volume_mounts_list,
                    ports=ports_list
                )
            )
        conditions_list = []
        for condition in deployment.status.conditions:
            conditions_list.append(
                dict(
                    last_transition_time=condition.last_transition_time,
                    last_update_time=condition.last_update_time,
                    message=condition.message,
                    reason=condition.reason,
                    status=condition.status,
                    type=condition.type
                )
            )
        deployment = dict(
            name=deployment.metadata.name,
            namespace=deployment.metadata.namespace,
            selector=dict(
                matchExpressions=deployment.spec.selector.match_expressions,
                matchLabels=deployment.spec.selector.match_labels,
            ),
            labels=deployment.metadata.labels,
            creationTimestamp=datetime.strftime(deployment.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            # serviceAccount=pod.spec.serviceAccount,
            # volumes=json.pod.spec.volumes,
            containers=containers_list,
            status=dict(
                available_replicas=deployment.status.available_replicas,
                conditions=conditions_list,
                ready_replicas=deployment.status.ready_replicas,
                replicas=deployment.status.replicas,
                unavailable_replicas=deployment.status.unavailable_replicas,
                updated_replicas=deployment.status.updated_replicas
            )
        )

        return Response(data={'data': deployment}, status=status.HTTP_200_OK)
