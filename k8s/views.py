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

        data = {
            'code': 20000,
            'data': nodes_list
        }
        return Response(data=data)


class NodeInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        name = request.query_params['name']
        logger.info(name)
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
        data = {
            'code': 20000,
            'data': node
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
                    creationTimestamp=datetime.strftime(namespace.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
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
                    nodename=pod.spec.node_name,
                    hostIP=pod.status.host_ip,
                    podIP=pod.status.pod_ip,
                    startTime=datetime.strftime(pod.status.start_time, '%Y-%m-%d %H:%M')
                )
            )
        data = {
            'code': 20000,
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
                        config_map=volume.config_map,
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
            'code': 20000,
            'data': pod
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
        data = {
            'code': 20000,
            'data': deployments_list
        }
        return Response(data=data)


class DeploymentInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.AppsV1Api()
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
        data = {
            'code': 20000,
            'data': deployment
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
                    ),
                    # status = f"{daemonset.status.number_ready}/{daemonset.status.replicas}"
                )
            )
        data = {
            'code': 20000,
            'data': daemonsets_list
        }
        return Response(data=data)


class DaemonsetInfo(APIView):
    pass


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
                    # status=dict(
                    #     collision_count=statefulset.status.collision_count,
                    #     current_replicas=statefulset.status.current_replicas,
                    #     replicas=statefulset.status.replicas,
                    #     updated_replicas=statefulset.status.updated_replicas,
                    # ),
                    status=f"{statefulset.status.current_replicas}/{statefulset.status.replicas}"
                )
            )
        data = {
            'code': 20000,
            'data': statefulsets_list
        }
        return Response(data=data)


class StatefulsetInfo(APIView):
    pass


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


class ServiceInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
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
        data = {
            'code': 20000,
            'data': service
        }
        return Response(data=data)


class IngressList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.NetworkingV1beta1Api()
        ingresses_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            ingresses = api.list_ingress_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            ingresses = api.list_namespaced_ingress(namespace=query_ns).items
        logger.info(f"Getting ingresses Total: {len(ingresses)} ingresses")
        for ingress in ingresses:
            ingresses_list.append(
                dict(
                    name=ingress.metadata.name,
                    namespace=ingress.metadata.namespace,
                    labels=ingress.metadata.labels,
                    creationTimestamp=datetime.strftime(ingress.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': ingresses_list
        }
        return Response(data=data)


class NetworkPolicyList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.NetworkingV1Api()
        networkpolicies_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            networkpolicies = api.list_network_policy_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            networkpolicies = api.list_namespaced_network_policy(namespace=query_ns).items
        logger.info(f"Getting networkpolicies Total: {len(networkpolicies)} networkpolicies")
        for networkpolicy in networkpolicies:
            networkpolicies_list.append(
                dict(
                    name=networkpolicy.metadata.name,
                    namespace=networkpolicy.metadata.namespace,
                    labels=networkpolicy.metadata.labels,
                    creationTimestamp=datetime.strftime(networkpolicy.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': networkpolicies_list
        }
        return Response(data=data)


class CronjobList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.BatchV1beta1Api()
        cronjobs_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            cronjobs = api.list_cron_job_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            cronjobs = api.list_namespaced_cron_job(namespace=query_ns).items
        logger.info(f"Getting cronjobs Total: {len(cronjobs)} cronjobs")
        for cronjob in cronjobs:
            cronjobs_list.append(
                dict(
                    name=cronjob.metadata.name,
                    namespace=cronjob.metadata.namespace,
                    labels=cronjob.metadata.labels,
                    creationTimestamp=datetime.strftime(cronjob.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    selector=cronjob.spec.selector,
                )
            )
        data = {
            'code': 20000,
            'data': cronjobs_list
        }
        return Response(data=data)


class JobList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.BatchV1Api()
        jobs_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            jobs = api.list_job_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            jobs = api.list_namespaced_job(namespace=query_ns).items
        logger.info(f"Getting jobs Total: {len(jobs)} jobs")
        for job in jobs:
            jobs_list.append(
                dict(
                    name=job.metadata.name,
                    namespace=job.metadata.namespace,
                    labels=job.metadata.labels,
                    creationTimestamp=datetime.strftime(job.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    selector=job.spec.selector,
                )
            )
        data = {
            'code': 20000,
            'data': jobs_list
        }
        return Response(data=data)


class ConfigMapList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
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
        data = {
            'code': 20000,
            'data': configmaps_list
        }
        return Response(data=data)


class SecretList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
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
        data = {
            'code': 20000,
            'data': secrets_list
        }
        return Response(data=data)


class SecretInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
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
        data = {
            'code': 20000,
            'data': secret
        }
        return Response(data=data)


class PVList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        pvs_list = []
        pvs = api.list_persistent_volume().items
        logger.info(f"Getting pvs Total: {len(pvs)} pvs")
        for pv in pvs:
            pvs_list.append(
                dict(
                    name=pv.metadata.name,
                    namespace=pv.metadata.namespace,
                    labels=pv.metadata.labels,
                    creationTimestamp=datetime.strftime(pv.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': pvs_list
        }
        return Response(data=data)


class PVCList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All services")
            pvcs = api.list_persistent_volume_claim_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            pvcs = api.list_namespaced_persistent_volume_claim(namespace=query_ns).items
        pvcs_list = []
        logger.info(f"Getting pvcs Total: {len(pvcs)} pvcs")
        for pvc in pvcs:
            pvcs_list.append(
                dict(
                    name=pvc.metadata.name,
                    namespace=pvc.metadata.namespace,
                    labels=pvc.metadata.labels,
                    creationTimestamp=datetime.strftime(pvc.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                    access_modes=pvc.spec.access_modes,
                    status=pvc.status.phase,
                    capacity=pvc.status.capacity,
                    volume_mode=pvc.spec.volume_mode,
                    storage_class_name=pvc.spec.storage_class_name
                )
            )
        data = {
            'code': 20000,
            'data': pvcs_list
        }
        return Response(data=data)


class ServiceAccountList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        pvs_list = []
        pvs = api.list_persistent_volume().items
        logger.info(f"Getting pvs Total: {len(pvs)} pvs")
        for pv in pvs:
            pvs_list.append(
                dict(
                    name=pv.metadata.name,
                    namespace=pv.metadata.namespace,
                    labels=pv.metadata.labels,
                    creationTimestamp=datetime.strftime(pv.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': pvs_list
        }
        return Response(data=data)


class RoleList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All roles")
            roles = api.list_role_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            roles = api.list_namespaced_role(namespace=query_ns).items
        logger.info(f"Getting roles Total: {len(roles)} roles")
        roles_list = []
        for role in roles:
            roles_list.append(
                dict(
                    name=role.metadata.name,
                    namespace=role.metadata.namespace,
                    labels=role.metadata.labels,
                    creationTimestamp=datetime.strftime(role.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': roles_list
        }
        return Response(data=data)


class RoleInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        name = request.query_params['name']
        namespace = request.query_params['namespace']
        role = api.read_namespaced_role(name=name, namespace=namespace)
        role = dict(
            name=role.metadata.name,
            namespace=role.metadata.namespace,
            labels=role.metadata.labels,
            creationTimestamp=datetime.strftime(role.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            rules=[
                dict(
                    api_groups=rule.api_groups,
                    non_resource_ur_ls=rule.non_resource_ur_ls,
                    resource_names=rule.resource_names,
                    resources=rule.resources,
                    verbs=rule.verbs
                ) for rule in role.rules
            ]
        )
        data = {
            'code': 20000,
            'data': role
        }
        return Response(data=data)


class RoleBindingList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All rolebindings")
            rolebindings = api.list_role_binding_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            rolebindings = api.list_namespaced_role(namespace=query_ns).items
        logger.info(f"Getting rolebindings Total: {len(rolebindings)} rolebindings")
        rolebindings_list = []
        for rolebinding in rolebindings:
            rolebindings_list.append(
                dict(
                    name=rolebinding.metadata.name,
                    namespace=rolebinding.metadata.namespace,
                    labels=rolebinding.metadata.labels,
                    creationTimestamp=datetime.strftime(rolebinding.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': rolebindings_list
        }
        return Response(data=data)


class RoleBindingInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        name = request.query_params['name']
        namespace = request.query_params['namespace']
        rolebinding = api.read_namespaced_role_binding(name=name, namespace=namespace)
        rolebinding = dict(
            name=rolebinding.metadata.name,
            namespace=rolebinding.metadata.namespace,
            labels=rolebinding.metadata.labels,
            creationTimestamp=datetime.strftime(rolebinding.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            role_ref=dict(
                api_group=rolebinding.role_ref.api_group,
                kind=rolebinding.role_ref.kind,
                name=rolebinding.role_ref.name
            ),
            subjects=[
                dict(
                    api_group=subject.api_group,
                    kind=subject.kind,
                    name=subject.name,
                    namespace=subject.namespace
                ) for subject in rolebinding.subjects
            ]
        )
        data = {
            'code': 20000,
            'data': rolebinding
        }
        return Response(data=data)


class ClusterRoleList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        clusterroles = api.list_cluster_role().items
        logger.info(f"Getting clusterroles Total: {len(clusterroles)} clusterroles")
        clusterroles_list = []
        for clusterrole in clusterroles:
            clusterroles_list.append(
                dict(
                    name=clusterrole.metadata.name,
                    namespace=clusterrole.metadata.namespace,
                    labels=clusterrole.metadata.labels,
                    creationTimestamp=datetime.strftime(clusterrole.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': clusterroles_list
        }
        return Response(data=data)


class ClusterRoleInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        name = request.query_params['name']
        role = api.read_cluster_role(name=name)
        role = dict(
            name=role.metadata.name,
            namespace=role.metadata.namespace,
            labels=role.metadata.labels,
            creationTimestamp=datetime.strftime(role.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            rules=[
                dict(
                    api_groups=rule.api_groups,
                    non_resource_ur_ls=rule.non_resource_ur_ls,
                    resource_names=rule.resource_names,
                    resources=rule.resources,
                    verbs=rule.verbs
                ) for rule in role.rules
            ]
        )
        data = {
            'code': 20000,
            'data': role
        }
        return Response(data=data)


class ClusterRoleBindingList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        clusterrolebindings = api.list_cluster_role_binding().items
        logger.info(f"Getting rolebindings Total: {len(clusterrolebindings)} rolebindings")
        clusterrolebindings_list = []
        for clusterrolebinding in clusterrolebindings:
            clusterrolebindings_list.append(
                dict(
                    name=clusterrolebinding.metadata.name,
                    namespace=clusterrolebinding.metadata.namespace,
                    labels=clusterrolebinding.metadata.labels,
                    creationTimestamp=datetime.strftime(clusterrolebinding.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
                )
            )
        data = {
            'code': 20000,
            'data': clusterrolebindings_list
        }
        return Response(data=data)


class ClusterRoleBindingInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.RbacAuthorizationV1Api()
        name = request.query_params['name']
        clusterrolebinding = api.read_cluster_role_binding(name=name)
        clusterrolebinding = dict(
            name=clusterrolebinding.metadata.name,
            namespace=clusterrolebinding.metadata.namespace,
            labels=clusterrolebinding.metadata.labels,
            creationTimestamp=datetime.strftime(clusterrolebinding.metadata.creation_timestamp, '%Y-%m-%d %H:%M'),
            role_ref=dict(
                api_group=clusterrolebinding.role_ref.api_group,
                kind=clusterrolebinding.role_ref.kind,
                name=clusterrolebinding.role_ref.name
            ),
            subjects=[
                dict(
                    api_group=subject.api_group,
                    kind=subject.kind,
                    name=subject.name,
                    namespace=subject.namespace
                ) for subject in clusterrolebinding.subjects
            ]
        )
        data = {
            'code': 20000,
            'data': clusterrolebinding
        }
        return Response(data=data)


class EventList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        events_list = []
        if 'namespace' not in request.query_params.dict():
            logger.info("No namespace Param, Getting All events")
            events = api.list_event_for_all_namespaces().items
        else:
            query_ns = request.query_params['namespace']
            events = api.list_namespaced_event(namespace=query_ns).items
        logger.info(f"Getting events Total: {len(events)} events")
        for event in events:
            events_list.append(
                dict(
                    name=event.metadata.name,
                    namespace=event.metadata.namespace,
                    labels=event.metadata.labels,
                    lastTimestamp=datetime.strftime(event.last_timestamp, '%Y-%m-%d %H:%M') if event.last_timestamp else '',
                    message=event.message,
                    reason=event.reason,
                    source=dict(
                        component=event.source.component,
                        host=event.source.host
                    ),
                    type=event.type
                )
            )
        data = {
            'code': 20000,
            'data': events_list
        }
        return Response(data=data)


class EventInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        config.load_kube_config()
        api = client.CoreV1Api()
        name = request.query_params['name']
        namespace = request.query_params['namespace']
        event = api.read_namespaced_event(name=name, namespace=namespace)
        event = dict(
            name=event.metadata.name,
            namespace=event.metadata.namespace,
            labels=event.metadata.labels,
            lastTimestamp=datetime.strftime(event.last_timestamp, '%Y-%m-%d %H:%M'),
            firstTimestamp=datetime.strftime(event.first_timestamp, '%Y-%m-%d %H:%M'),
            creationTimestamp=datetime.strftime(event.creation_timestamp, '%Y-%m-%d %H:%M'),
            message=event.message,
            source=dict(
                component=event.source.component,
                host=event.source.host
            ),
            type=event.type,
            involved_object=dict(
                field_path=event.involved_object.field_path,
                kind=event.involved_object,
                name=event.involved_object,
                namespace=event.involved_object,
            )
        )
        data = {
            'code': 20000,
            'data': event
        }
        return Response(data=data)
