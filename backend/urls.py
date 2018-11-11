"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import RiskTypeViewSet, RiskViewSet

schema_view = get_schema_view(
    openapi.Info(
        title="Risk Management API",
        default_version='v1',
        description="API for Britecore Product Development Project",
    ),
    public=True,
)

router = routers.DefaultRouter()
router.register("risk_types", RiskTypeViewSet)
router.register("risks", RiskViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='swagger_docs'),
]
