from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger

from kubernetes import config,client

class PodList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        pods_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All pods")
            pods = api.list_pod_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            pods = api.list_namespaced_pod(namespace=query_ns).items
        logger.info(f"Getting pods Total: {len(pods)} Pods")
        for pod in pods:
            container_statuses_list = []
            if pod.status.container_statuses:
                for container_status in pod.status.container_statuses:
                    container_statuses_list.append(
                        dict(
                            name=container_status.name,
                            ready=container_status.ready,
                            restart_count=container_status.restart_count,
                            started=container_status.started,
                            container_id=container_status.container_id,
                            image=container_status.image,
                            # last_state=dict(
                            #     running=container_status.last_state.running,
                            #     terminated=dict(
                            #         exit_code=container_status.last_state.terminated.exit_code,
                            #         finished_at=container_status.last_state.terminated.finished_at,
                            #         message=container_status.last_state.terminated.message,
                            #         reason=container_status.last_state.terminated.reason,
                            #         started_at=container_status.last_state.terminated.started_at
                            #     ),
                            #     waiting=container_status.last_state.waiting
                            # ),
                            # state=dict(
                            #     running=container_status.state.running,
                            #     terminated=container_status.state.terminated,
                            #     waiting=container_status.state.waiting
                            # )
                        )
                    )

            pods_list.append(
                dict(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    labels=pod.metadata.labels,
                    creationTimestamp=datetime.strftime(pod.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    nodename=pod.spec.node_name,
                    hostIP=pod.status.host_ip,
                    podIP=pod.status.pod_ip,
                    startTime=datetime.strftime(pod.status.start_time, '%Y-%m-%d %H:%M'),
                    container_statuses=container_statuses_list
                )
            )
        data = {
            'code': 200,
            'data': pods_list
        }
        return Response(data=data)


class PodInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        name = request.query_params['name']
        namespace = request.query_params['namespace']
        pod = api.read_namespaced_pod(name=name, namespace=namespace)
        containers_list = []
        for container in pod.spec.containers:
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
        volumes_list = []
        if pod.spec.volumes:
            for volume in pod.spec.volumes:
                volumes_list.append(
                    dict(
                        name=volume.name,
                        empty_dir=volume.empty_dir,
                        csi=volume.csi,
                        config_map=dict(
                            default_mode=volume.config_map.default_mode if volume.config_map.default_mode else '',
                    #        items=[dict(
                    #            key=item.key,
                    #            mode=item.mode,
                    #            path=item.path
                    #        ) for item in volume.config_map.items],
                            name=volume.config_map.name,
                            optional=volume.config_map.optional
                        ) if volume.config_map else '',
                        host_path=volume.host_path,
                        nfs=volume.nfs,
                        persistent_volume_claim=volume.persistent_volume_claim,
                    )
                )
        else:
            volumes_list = []
        conditions_list = []
        if pod.status.conditions:
            for condition in pod.status.conditions:
                conditions_list.append(
                    dict(
                        last_probe_time=condition.last_probe_time,
                        last_transition_time=datetime.strftime(condition.last_transition_time, '%Y-%m-%d %H:%M'),
                        message=condition.message,
                        status=condition.status,
                        type=condition.type
                    )
                )
        else:
            conditions_list = []
        container_statuses_list = []
        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                container_statuses_list.append(
                    dict(
                        name=container_status.name,
                        ready=container_status.ready,
                        restart_count=container_status.restart_count,
                        started=container_status.started,
                        container_id=container_status.container_id,
                        image=container_status.image,
                        # last_state=dict(
                        #     running=container_status.last_state.running,
                        #     terminated=dict(
                        #         exit_code=container_status.last_state.terminated.exit_code,
                        #         finished_at=container_status.last_state.terminated.finished_at,
                        #         message=container_status.last_state.terminated.message,
                        #         reason=container_status.last_state.terminated.reason,
                        #         started_at=container_status.last_state.terminated.started_at
                        #     ),
                        #     waiting=container_status.last_state.waiting
                        # ),
                        # state=dict(
                        #     running=container_status.state.running,
                        #     terminated=container_status.state.terminated,
                        #     waiting=container_status.state.waiting
                        # )
                    )
                )
        owner_references_list = []
        for owner_reference in pod.metadata.owner_references:
            owner_references_list.append(
                dict(
                    api_version=owner_reference.api_version,
                    block_owner_deletion=owner_reference.block_owner_deletion,
                    controller=owner_reference.controller,
                    kind=owner_reference.kind,
                    name=owner_reference.name
                )
            )

        pod = dict(
            name=pod.metadata.name,
            namespace=pod.metadata.namespace,
            labels=pod.metadata.labels,
            ownerReferences=owner_references_list,
            creationTimestamp=datetime.strftime(pod.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            hostname=pod.spec.hostname,
            nodename=pod.spec.node_name,
            dnsPolicy=pod.spec.dns_policy,
            restartPolicy=pod.spec.restart_policy,
            containers=containers_list,
            # serviceAccount=pod.spec.serviceAccount,
            volumes=volumes_list,
            hostIP=pod.status.host_ip,
            podIP=pod.status.pod_ip,
            startTime=datetime.strftime(pod.status.start_time, '%Y-%m-%d %H:%M'),
            conditions=conditions_list,
            container_statuses=container_statuses_list
        )
        data = {
            'code': 200,
            'data': pod
        }
        return Response(data=data)

