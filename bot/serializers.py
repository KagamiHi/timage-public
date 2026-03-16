from rest_framework import serializers

from bot.models import ImageModel, Reaction
from common.utils.serializers import EagerSerializerModel


class ImageSerializer(EagerSerializerModel):
    url = serializers.ReadOnlyField(source="external_url")

    class Meta:
        model = ImageModel
        fields = [
            "id",
            "url",
        ]
        read_only_fields = fields


class ReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = ["react"]

    def create(self, validated_data):
        user = self.context["request"].user
        image = self.context["image"]
        return Reaction.objects.update_or_create(user=user, image=image, defaults=validated_data)
