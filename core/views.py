from rest_framework import viewsets, mixins

from core.models import RiskType, Risk
from core.serializers import (RiskTypeSerializer, RiskTypeListSerializer,
                              RiskSerializer)


class RiskTypeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.ReadOnlyModelViewSet):
    queryset = RiskType.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RiskTypeListSerializer
        return RiskTypeSerializer


class RiskViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.ReadOnlyModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
