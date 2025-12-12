from rest_framework import serializers


class FKOptionsCacheSerializer(serializers.Serializer):
    field = serializers.CharField()
    options = serializers.ListField(child=serializers.DictField())
    count = serializers.IntegerField()
    cache_age = serializers.CharField(required=False, allow_null=True)
    factories_count = serializers.IntegerField(required=False)

