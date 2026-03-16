"""
URL configuration for timage project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import token_obtain_pair, token_refresh

from backend.settings import DEBUG, COMMIT_HASH
from bot.views import SwipesViewSet
from users.auth import tlg_token_obtain_pair


@api_view()
@permission_classes((permissions.AllowAny,))
def health_view(*args, **kwargs):
    return Response()


router = DefaultRouter(trailing_slash=True)
router.register("swipes", SwipesViewSet, "swipes")

urlpatterns = [
    path("health/", health_view),
    path("api/", include(router.urls)),
    path("api/tlg-token/", tlg_token_obtain_pair, name="tlg_token_obtain_pair"),
    path("api/token/", token_obtain_pair, name="token_obtain_pair"),
    path("api/token/refresh/", token_refresh, name="token_refresh"),
    re_path(
        "",
        TemplateView.as_view(
            template_name="index.html",
            extra_context=dict(
                debug=DEBUG,
                hash=COMMIT_HASH,
            ),
        ),
    ),
    *staticfiles_urlpatterns(),
]
