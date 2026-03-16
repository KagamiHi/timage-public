from django.db.models import QuerySet
from rest_framework import serializers


class EagerSerializerModel(serializers.ModelSerializer):

    @staticmethod
    def setup_eager_loading(queryset: QuerySet) -> QuerySet:
        return queryset
