from django.db.models import Q
from drf_haystack.filters import HaystackFilter, HaystackOrderingFilter
from drf_haystack.viewsets import HaystackViewSet
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from drf_multiple_model.views import ObjectMultipleModelAPIView

from apps.goods.models import Goods, Banner
from apps.goods.serializers import GoodsSerializer, BannerSerializer, GoodsSearchSerializers
from utils.key_constructor import GoodsListKeyConstructor, GoodsObjectKeyConstructor


class GoodsViewSet(CacheResponseMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取商品信息列表
    retrieve:
        获取商品详情
    """

    serializer_class = GoodsSerializer
    queryset = Goods.objects.all()
    object_cache_key_func = GoodsObjectKeyConstructor()
    list_cache_key_func = GoodsListKeyConstructor()


class GoodsSearchView(HaystackViewSet):
    index_models = [Goods]
    serializer_class = GoodsSearchSerializers
    filter_backends = [HaystackFilter, HaystackOrderingFilter]
    ordering_fields = ('price',)


class HomeView(ObjectMultipleModelAPIView):
    """
    首页接口
    """
    querylist = [
        {'queryset': Banner.objects.all(), 'serializer_class': BannerSerializer},
        {
            'queryset': Goods.objects.filter(Q(is_hot=True) | Q(is_new=True))[:8],
            'serializer_class': GoodsSerializer
        }
    ]
    pagination_class = MultipleModelLimitOffsetPagination
