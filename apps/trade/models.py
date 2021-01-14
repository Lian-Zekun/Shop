import random
import time
from datetime import timedelta

from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.goods.models import Goods
from apps.users.models import UserAddress

User = get_user_model()


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    nums = models.IntegerField(default=1, verbose_name='商品数量')
    checked = models.BooleanField(default=False, verbose_name='是否选中')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']
        indexes = [
            models.Index(fields=['goods'], name='cart_goods_idx'),
        ]

    def __str__(self):
        return f'{self.user}-{self.goods.name}-{self.nums}-{self.checked}'


class OrderInfo(models.Model):

    class OrderStatus(models.IntegerChoices):
        UNPAID = 1
        PAID = 2
        SUCCESS = 3
        CANCEL = 4
        INVALID = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    # unique订单号唯一
    order_sn = models.CharField(default='', max_length=30, unique=True, verbose_name='订单编号')
    order_status = models.IntegerField(default=1, choices=OrderStatus.choices, verbose_name='订单状态')
    # 订单的支付类型、未使用
    pay_type = models.IntegerField(default=0, verbose_name='支付类型')
    order_message = models.CharField(max_length=200, default='', verbose_name='订单留言')
    order_amount = models.FloatField(default=0.0, verbose_name='订单金额')
    # 用户的基本信息
    address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, verbose_name='地址')
    pay_time = models.DateTimeField(default=timezone.now, verbose_name='支付时间')
    end_time = models.DateTimeField(default=timezone.now, verbose_name='订单取消或完成时间')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']
        indexes = [
            models.Index(fields=['order_status'], name='order_status_idx')
        ]

    def recover_goods_stock(self):
        order_goods = OrderGoods.objects.filter(order=self)
        for order_g in order_goods:
            goods = order_g.goods
            goods.stock += order_g.nums
            goods.save()

    def is_invalid_order(self):
        if self.order_status != self.OrderStatus.UNPAID:
            return False
        diff = int(round(time.time() * 1000)) - int(round(self.ctime.timestamp() * 1000))
        return diff > 60 * 60 * 1000

    @transaction.atomic
    def invalid_order_handle(self):
        self.order_status = self.OrderStatus.CANCEL
        self.recover_goods_stock()
        self.end_time = self.ctime + timedelta(hours=1)
        self.save()

    @staticmethod
    def generate_order_sn():
        order_sn = '{timestamp}{randstr:0>2d}'.format(timestamp=int(round(time.time() * 1000)),
                                                      randstr=random.randint(0, 99))
        return order_sn

    def save(self, *args, **kwargs):
        if not self.order_sn:
            self.order_sn = self.generate_order_sn()
        super(OrderInfo, self).save(*args, **kwargs)

    def __str__(self):
        return self.order_sn


class OrderGoods(models.Model):
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, related_name='order_goods', verbose_name='订单信息')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    nums = models.IntegerField(default=1, verbose_name='商品数量')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']
        indexes = [
            models.Index(fields=['order'], name='order_idx'),
            models.Index(fields=['goods'], name='order_goods_idx')
        ]

    def __str__(self):
        return self.order.order_sn
