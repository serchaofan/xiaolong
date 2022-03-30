from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class PVList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
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

        return Response(data={'data': pvs_list}, status=status.HTTP_200_OK)


class PVCList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
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

        return Response(data={'data': pvcs_list}, status=status.HTTP_200_OK)
