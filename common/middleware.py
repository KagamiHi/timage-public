class LocalAuthMiddleware:
    """Authenticate every request as the local fixture user (only added to MIDDLEWARE when LOCAL=1)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import json
        from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.http import JsonResponse
        from users.models import User
        try:
            user = User.objects.get(tlg_id=1)
        except User.DoesNotExist:
            return self.get_response(request)
        request.user = user
        if request.path == "/api/tlg-token/":
            refresh: RefreshToken = TokenObtainPairSerializer().get_token(user)  # noqa
            return JsonResponse({"refresh": str(refresh), "access": str(refresh.access_token)})
        return self.get_response(request)
