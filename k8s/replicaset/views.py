from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger

from kubernetes import config,client

class ReplicasetList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.AppsV1Api()
        replicasets_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All replicasets")
            replicasets = api.list_replica_set_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            replicasets = api.list_namespaced_replica_set(namespace=query_ns).items
        logger.info(f"Getting replicasets Total: {len(replicasets)} replicasets")
        for replicaset in replicasets:
            containers_list = []
            for container in replicaset.spec.template.spec.containers:
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
            replicasets_list.append(
                dict(
                    name=replicaset.metadata.name,
                    namespace=replicaset.metadata.namespace,
                    selector=dict(
                        matchExpressions=replicaset.spec.selector.match_expressions,
                        matchLabels=replicaset.spec.selector.match_labels,
                    ),
                    labels=replicaset.metadata.labels,
                    creationTimestamp=datetime.strftime(replicaset.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    containers=containers_list,
                    # status=dict(
                    #     available_replicas=replicaset.status.available_replicas,
                    #     fully_labeled_replicas=replicaset.status.fully_labeled_replicas,
                    #     ready_replicas=replicaset.status.ready_replicas,
                    #     replicas=replicaset.status.replicas,
                    # ),
                    status=f"{replicaset.status.ready_replicas}/{replicaset.status.replicas}" if replicaset.status.ready_replicas else "NULL"
                )
            )
        data = {
            'code': 20000,
            'data': replicasets_list
        }
        return Response(data=data)


class ReplicasetInfo(APIView):
    pass
