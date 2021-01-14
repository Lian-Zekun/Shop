from django.contrib import admin

from apps.trade.models import ShoppingCart, OrderInfo, OrderGoods


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'goods', 'nums', 'ctime']
    list_filter = ['user']
    search_fields = ['user']


@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'order_sn',  'order_status', 'order_amount', 'pay_time', 'end_time', 'ctime']
    list_filter = ['user']
    search_fields = ['user']

    class OrderGoodsInline(admin.TabularInline):
        model = OrderGoods
        exclude = ['ctime']

    inlines = [OrderGoodsInline]
