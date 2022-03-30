from django.db import models
from jsonfield import JSONField

class Cluster(models.Model):
    name = models.CharField(max_length=255)
    desciption = models.CharField(max_length=255)
    kubeconfig = JSONField()

    def __str__(self) -> str:
        return str(self.name)