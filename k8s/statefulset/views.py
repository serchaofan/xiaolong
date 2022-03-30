from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client

class StatefulsetList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.AppsV1Api(api_client=api_client)
        statefulsets_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All statefulsets")
            statefulsets = api.list_stateful_set_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            statefulsets = api.list_namespaced_stateful_set(namespace=query_ns).items
        logger.info(f"Getting statefulsets Total: {len(statefulsets)} statefulsets")
        for statefulset in statefulsets:
            containers_list = []
            for container in statefulset.spec.template.spec.containers:
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
                        command=container.command,
                        args=container.args,
                        env=envs_list,
                        image=container.image,
                        image_pull_policy=container.image_pull_policy,
                        resources=dict(
                            limits=container.resources.limits,
                            requests=container.resources.requests
                        ),
                        volume_mounts=volume_mounts_list,
                        ports=ports_list
                    )
                )
            statefulsets_list.append(
                dict(
                    name=statefulset.metadata.name,
                    namespace=statefulset.metadata.namespace,
                    selector=dict(
                        matchExpressions=statefulset.spec.selector.match_expressions,
                        matchLabels=statefulset.spec.selector.match_labels,
                    ),
                    labels=statefulset.metadata.labels,
                    creationTimestamp=datetime.strftime(statefulset.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    containers=containers_list,
                    # status=dict(
                    #     collision_count=statefulset.status.collision_count,
                    #     current_replicas=statefulset.status.current_replicas,
                    #     replicas=statefulset.status.replicas,
                    #     updated_replicas=statefulset.status.updated_replicas,
                    # ),
                    status=f"{statefulset.status.current_replicas}/{statefulset.status.replicas}"
                )
            )

        return Response(data={'data': statefulsets_list}, status=status.HTTP_200_OK)


class StatefulsetInfo(APIView):
    pass
