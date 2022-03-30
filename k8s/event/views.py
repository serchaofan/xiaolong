from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime
from loguru import logger
import rest_framework.status as status
from ..views import get_k8s_api_client
from kubernetes import client


class EventList(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
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

        return Response(data={'data': events_list}, status=status.HTTP_200_OK)


class EventInfo(APIView):
    @staticmethod
    def get(request, *args, **kwargs):
        api_client = get_k8s_api_client(request=request)
        if api_client == 400:
            return Response({"data": "Cluster Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)
        api = client.CoreV1Api(api_client=api_client)
        if 'name' not in request.query_params.dict() or 'namespace' not in request.query_params.dict():
            return Response({"data": "Name Or Namespace Param ERROR"}, status=status.HTTP_400_BAD_REQUEST)

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

        return Response(data={'data': event}, status=status.HTTP_200_OK)
