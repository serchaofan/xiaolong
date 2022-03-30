from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class ServiceAccountList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        pass

class RoleList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
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

        return Response(data={'data': roles_list}, status=status.HTTP_200_OK)


class RoleInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
        if 'name' not in request.query_params.dict() or 'namespace' not in request.query_params.dict():
            return Response({"data": "Name Or Namespace Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(data={'data': role}, status=status.HTTP_200_OK)


class RoleBindingList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
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

        return Response(data={'data': rolebindings_list}, status=status.HTTP_200_OK)


class RoleBindingInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
        if 'name' not in request.query_params.dict() or 'namespace' not in request.query_params.dict():
            return Response({"data": "Name Or Namespace Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(data={'data': rolebinding}, status=status.HTTP_200_OK)


class ClusterRoleList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
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

        return Response(data={'data': clusterroles_list}, status=status.HTTP_200_OK)


class ClusterRoleInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)

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

        return Response(data={'data': role}, status=status.HTTP_200_OK)


class ClusterRoleBindingList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
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

        return Response(data={'data': clusterrolebindings_list}, status=status.HTTP_200_OK)


class ClusterRoleBindingInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.RbacAuthorizationV1Api(api_client=api_client)
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

        return Response(data={'data': clusterrolebinding}, status=status.HTTP_200_OK)
