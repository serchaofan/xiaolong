from rest_framework.response import Response

from kubernetes import config, client
from rest_framework.views import APIView
from loguru import logger
import json
from datetime import datetime


class NodeList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        nodes_list = []
        nodes = api.list_node().items
        for node in nodes:
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
                            names=image.names,
                            size_bytes=image.size_bytes
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

            nodes_list.append(dict(
                name=node.metadata.name,
                podCidr=node.spec.pod_cidr,
                capacity=node.status.capacity,
                allocatable=node.status.allocatable,
                labels=node.metadata.labels,
                annotations=node.metadata.annotations,
                creationTimestamp=datetime.strftime(node.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                # creationTimestamp=node.metadata.creation_timestamp,
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
                role=node.metadata.labels['kubernetes.io/role'],
                kubelet_version=node.status.node_info.kubelet_version,
                conditions=conditions_list,
                status=conditions_list[-1]['type'] if conditions_list[-1]['status']=='True' else 'NotReady',
                images=images_list,
                addresses=addresses_list,
                taints=taints_list,
                unschedulable=node.spec.unschedulable,
                daemonEndpoints=dict(
                    kubelet_endpoint=dict(port=node.status.daemon_endpoints.kubelet_endpoint.port),
                )
            ))

        data = {
            'code': 20000,
            'data': nodes_list
        }
        return Response(data=data)


class NamespaceList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
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
            pods_list.append(
                dict(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    labels=pod.metadata.labels,
                    creationTimestamp=datetime.strftime(pod.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
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
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.AppsV1Api()
        deployments_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All deployments")
            deployments = api.list_deployment_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            deployments = api.list_namespaced_deployment(namespace=query_ns).items
        logger.info(f"Getting deployments Total: {len(deployments)} deployments")
        for deployment in deployments:
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
            deployments_list.append(
                dict(
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
            )
        data = {
            'code': 20000,
            'data': deployments_list
        }
        return Response(data=data)


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
                    )
                )
            )
        data = {
            'code': 20000,
            'data': daemonsets_list
        }
        return Response(data=data)


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
                    status=dict(
                        available_replicas=replicaset.status.available_replicas,
                        fully_labeled_replicas=replicaset.status.fully_labeled_replicas,
                        ready_replicas=replicaset.status.ready_replicas,
                        replicas=replicaset.status.replicas,
                    )
                )
            )
        data = {
            'code': 20000,
            'data': replicasets_list
        }
        return Response(data=data)


class StatefulsetList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.AppsV1Api()
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
                    status=dict(
                        collision_count=statefulset.status.collision_count,
                        current_replicas=statefulset.status.current_replicas,
                        replicas=statefulset.status.replicas,
                        updated_replicas=statefulset.status.updated_replicas,
                    )
                )
            )
        data = {
            'code': 20000,
            'data': statefulsets_list
        }
        return Response(data=data)


class ServiceList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
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
        data = {
            'code': 20000,
            'data': services_list
        }
        return Response(data=data)