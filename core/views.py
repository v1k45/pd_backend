from rest_framework import viewsets

from core.models import RiskType
from core.serializers import RiskTypeSerializer, RiskTypeListSerializer


class RiskTypeViewSet(viewsets.ModelViewSet):
    queryset = RiskType.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RiskTypeListSerializer
        return RiskTypeSerializer
