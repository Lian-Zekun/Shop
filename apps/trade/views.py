from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import ShoppingCart, OrderInfo, OrderGoods
from .serializers import ShopCartSerializer, OrderSerializer, ShopCartDetailSerializer, OrderDetailSerializer
from utils.permissions import IsOwnerOrReadOnly
from ..goods.models import Goods


class ShoppingCartViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication,)
    pagination_class = None

    def get_queryset(self):
        return ShoppingCart.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ShopCartDetailSerializer
        return ShopCartSerializer

    @action(methods=['post'], detail=False)
    def update_all_checked(self, request, *args, **kwargs):
        checked = request.data['checked']
        queryset = self.filter_queryset(self.get_queryset())
        queryset.update(checked=checked)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=False)
    def delete_all_checked(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset.filter(checked=True).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderInfoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = OrderSerializer
    lookup_field = 'order_sn'

    def get_queryset(self):
        return OrderInfo.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderDetailSerializer
        return OrderSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        for instance in queryset:
            if instance.is_invalid_order():
                instance.invalid_order_handle()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_invalid_order():
            instance.invalid_order_handle()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        if self.request.data.get('goods_id'):
            self.create_single_goods_order(instance)
        else:
            self.create_shop_cart_order(instance)
        return instance

    def perform_destroy(self, instance):
        if instance.order_status in [OrderInfo.OrderStatus.UNPAID, OrderInfo.OrderStatus.PAID]:
            with transaction.atomic():
                instance.recover_goods_stock()
                instance.delete()
        else:
            instance.delete()

    def create_single_goods_order(self, instance):
        goods_id, nums = int(self.request.data.get('goods_id')), int(self.request.data.get('nums'))
        with transaction.atomic():
            try:
                goods = Goods.objects.get(pk=goods_id)
            except Goods.DoesNotExist:
                raise ValidationError(detail={'goods_id': ['商品不存在！']})
            self.goods_to_order_goods(instance, goods, nums)
            instance.order_amount = goods.price * nums
            instance.save()

    def create_shop_cart_order(self, instance):
        shop_carts = ShoppingCart.objects.filter(user=self.request.user)
        order_amount = 0
        with transaction.atomic():
            for shop_cart in shop_carts:
                if shop_cart.checked:
                    goods = shop_cart.goods
                    self.goods_to_order_goods(instance, goods, shop_cart.nums)
                    shop_cart.delete()
                    order_amount += goods.price * shop_cart.nums
            instance.order_amount = order_amount
            instance.save()

    @staticmethod
    def goods_to_order_goods(instance, goods, nums):
        if goods.stock < nums:
            raise ValidationError(detail={'error': [f'{goods.name}库存不足请重新选择！']})
        OrderGoods.objects.create(order=instance, goods=goods, nums=nums)
        goods.stock -= nums
        goods.save()

    # @staticmethod
    # def judge_order(instance):
    #     if instance.pay_status == 0:
    #         diff = int(round(time.time() * 1000)) - int(round(instance.ctime.timestamp() * 1000))
    #         if diff > 60 * 60 * 1000:
    #             with transaction.atomic():
    #                 instance.pay_status = 4
    #                 instance.recover_goods_stock()
    #                 instance.end_time = instance.ctime + timedelta(hours=1)
    #                 instance.save()
