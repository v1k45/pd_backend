from rest_framework import viewsets, mixins

from core.models import RiskType, Risk
from core.serializers import (RiskTypeSerializer, RiskTypeListSerializer,
                              RiskSerializer)


class RiskTypeViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.ReadOnlyModelViewSet):
    """
    API to create, view and delete risk types.

    list:
    Return list of risk types with only name and description

    retrieve:
    Return a risk type by id with field details

    create:
    Create a new risk type with along with fields and option values

    destroy:
    Delete a risk type by id
    """
    queryset = RiskType.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RiskTypeListSerializer
        return RiskTypeSerializer


class RiskViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.ReadOnlyModelViewSet):
    """
    API to create, view and delete risk objects.

    list:
    Return list of risk objects

    retrieve:
    Return a risk object by id

    create:
    Create a new risk object from a risk type template

    destroy:
    Delete a risk object by id
    """
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
