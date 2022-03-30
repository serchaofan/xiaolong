from dataclasses import fields
from rest_framework.serializers import ModelSerializer

from .models import Cluster

class ClusterModelSerializer(ModelSerializer):
    class Meta:
        model = Cluster
        fields = "__all__"