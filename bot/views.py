from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache

from bot.models import ImageModel
from bot.serializers import ImageSerializer, ReactionSerializer


class SwipesViewSet(GenericViewSet, ListModelMixin):
    queryset = ImageModel.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.request.user.recommend_for_user()

        # Cache the current batch of image IDs
        image_ids = [img_id.hex for img_id in queryset.values_list("id", flat=True)]
        if image_ids:
            prev = cache.get(f"user_batch:{request.user.id}") or []
            cache.set(f"user_batch:{request.user.id}", list(set(prev + image_ids))[-10:], timeout=3600)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=True)
    def react(self, request, *args, **kwargs):
        image = self.get_object()
        user = request.user
        serializer = ReactionSerializer(
            data=request.data, context={"request": request, "image": image}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if serializer.validated_data["react"]:
            try:
                user.send_tlg_message(image)
            except Exception as e:
                return Response("Error sending telegram message", status=500)
        return Response(status=201)
