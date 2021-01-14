from drf_haystack.serializers import HaystackSerializerMixin
from rest_framework import serializers

from apps.goods.models import Goods, Banner


class GoodsImageSerializer(serializers.Serializer):
    image = serializers.ImageField()


class GoodsSerializer(serializers.ModelSerializer):
    images = GoodsImageSerializer(read_only=True, many=True)

    class Meta:
        model = Goods
        fields = '__all__'


class GoodsSearchSerializers(HaystackSerializerMixin, GoodsSerializer):
    class Meta(GoodsSerializer.Meta):
        search_fields = ['text', 'price']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'
