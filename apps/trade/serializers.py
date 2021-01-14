from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.goods.models import Goods
from apps.trade.models import ShoppingCart, OrderGoods, OrderInfo
from apps.users.serializers import AddressSerializer


class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ('id', 'name', 'price', 'stock', 'goods_front_image')


class ShopCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(min_value=1,
                                    error_messages={
                                        'min_value': '商品数量不能小于一',
                                        'required': '请选择购买数量'
                                    })

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        extra_kwargs = {'checked': {'required': False}}

    def create(self, validated_data):
        try:
            instance = ShoppingCart.objects.get(user=validated_data['user'], goods=validated_data['goods'])
            instance.nums += validated_data['nums']
            instance.save()
        except ShoppingCart.DoesNotExist:
            instance = ShoppingCart.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):
        # 只允许更改 nums 以及 checked
        if validated_data['nums']:
            instance.nums = validated_data['nums']
        if isinstance(validated_data['checked'], bool):
            instance.checked = validated_data['checked']
        instance.save()
        return instance


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    order_status = serializers.IntegerField(min_value=1, max_value=4)

    class Meta:
        model = OrderInfo
        fields = '__all__'
        extra_kwargs = {
            'order_amount': {'read_only': True},
            'order_sn': {'read_only': True}
        }

    def create(self, validated_data):
        if validated_data['order_status'] != OrderInfo.OrderStatus.UNPAID:
            raise serializers.ValidationError(detail={'order_status': [
                f'创建时 order_status 值必须为 {OrderInfo.OrderStatus.UNPAID}']})
        return super(OrderSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        if instance.order_status not in [OrderInfo.OrderStatus.UNPAID, OrderInfo.OrderStatus.PAID]:
            return instance
        instance = super(OrderSerializer, self).update(instance, validated_data)
        order_status = validated_data.get('order_status', None)
        with transaction.atomic():
            if order_status == OrderInfo.OrderStatus.PAID:
                instance.pay_time = timezone.now()
            elif order_status != OrderInfo.OrderStatus.UNPAID:
                instance.end_time = timezone.now()
            if order_status == OrderInfo.OrderStatus.CANCEL:
                instance.recover_goods_stock()
            instance.save()
        return instance


class OrderDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    order_goods = OrderGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = OrderInfo
        fields = ['id', 'user', 'order_sn', 'order_status', 'pay_type', 'order_message', 'order_amount',
                  'address', 'pay_time', 'end_time', 'ctime', 'order_goods']
