from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class CronjobList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.BatchV1beta1Api(api_client=api_client)
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

        return Response(data={'data': cronjobs_list}, status=status.HTTP_200_OK)


class JobList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.BatchV1Api(api_client=api_client)
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

        return Response(data={'data': jobs_list}, status=status.HTTP_200_OK)
