from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger

from kubernetes import config,client


class DaemonsetList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.AppsV1Api()
        daemonsets_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All daemonsets")
            daemonsets = api.list_daemon_set_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            daemonsets = api.list_namespaced_daemon_set(namespace=query_ns).items
        logger.info(f"Getting daemonsets Total: {len(daemonsets)}")
        for daemonset in daemonsets:
            containers_list = []
            for container in daemonset.spec.template.spec.containers:
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
            daemonsets_list.append(
                dict(
                    name=daemonset.metadata.name,
                    namespace=daemonset.metadata.namespace,
                    selector=dict(
                        matchExpressions=daemonset.spec.selector.match_expressions,
                        matchLabels=daemonset.spec.selector.match_labels,
                    ),
                    labels=daemonset.metadata.labels,
                    creationTimestamp=datetime.strftime(daemonset.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    # serviceAccount=pod.spec.serviceAccount,
                    # volumes=json.pod.spec.volumes,
                    containers=containers_list,
                    status=dict(
                        current_number_scheduled=daemonset.status.current_number_scheduled,
                        desired_number_scheduled=daemonset.status.desired_number_scheduled,
                        number_available=daemonset.status.number_available,
                        number_misscheduled=daemonset.status.number_misscheduled,
                        number_ready=daemonset.status.number_ready,
                        number_unavailable=daemonset.status.number_unavailable,
                        updated_number_scheduled=daemonset.status.updated_number_scheduled,
                    ),
                    # status = f"{daemonset.status.number_ready}/{daemonset.status.replicas}"
                )
            )
        data = {
            'code': 200,
            'data': daemonsets_list
        }
        return Response(data=data)


class DaemonsetInfo(APIView):
    pass
