import json
from datetime import datetime, timezone
from urllib.parse import parse_qsl

from aiogram.utils.web_app import check_webapp_signature
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from users.models import User


class TlgAuthSerializer(serializers.Serializer):
    auth_data = serializers.CharField()

    def validate(self, attrs):
        auth_data_str = attrs["auth_data"]
        parsed_data = dict(parse_qsl(auth_data_str, strict_parsing=True))
        auth_date = datetime.fromtimestamp(int(parsed_data["auth_date"]), tz=timezone.utc)
        tlg_token = settings.TLG_BOT_TOKEN.split("/")[0] # to drop "/test" for test env
        if not check_webapp_signature(tlg_token, auth_data_str):
            msg = "Access denied: wrong auth_data."
            raise serializers.ValidationError(msg, code="authorization")
        elif (datetime.now(timezone.utc) - auth_date > settings.AUTH_DELAY_THRESHOLD) and (not settings.DEBUG):
            msg = "Access denied: its too late to auth."
            raise serializers.ValidationError(msg, code="authorization")
        user_data = User.patch_telegram_data(json.loads(parsed_data["user"]))
        user, _ = User.objects.update_or_create(tlg_id=user_data.pop("id"), defaults=user_data)
        # todo handle all fields from https://core.telegram.org/bots/webapps#webappuser
        refresh: RefreshToken = TokenObtainPairSerializer().get_token(user)  # noqa
        return dict(
            refresh=str(refresh),
            access=str(refresh.access_token)
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def tlg_token_obtain_pair(request: Request):
    serializer = TlgAuthSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.validated_data)
