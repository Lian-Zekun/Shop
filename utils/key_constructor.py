import os
from datetime import datetime

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete, pre_delete
from django.utils.encoding import force_text
from rest_framework_extensions.key_constructor.constructors import \
    DefaultObjectKeyConstructor, DefaultListKeyConstructor
from rest_framework_extensions.key_constructor.bits import KeyBitBase, UserKeyBit

from apps.goods.models import Goods, GoodsImage
from apps.trade.models import ShoppingCart, OrderInfo
from apps.users.models import User, UserAddress


class UpdatedAtKeyBit(KeyBitBase):
    def get_data(self, params, view_instance, view_method, request, args, kwargs):
        key = f'{view_instance.__class__.__name__}_updated_at'
        return self._get_data(key)

    def _get_data(self, key):
        value = cache.get(key, None)
        if not value:
            value = datetime.utcnow()
            cache.set(key, value)
        return force_text(value)


# class HomeUpdatedAtKeyBit(UpdatedAtKeyBit):
#     def get_data(self, params, view_instance, view_method, request, args, kwargs):
#         key = 'HomeViewSet_updated_at'
#         return self._get_data(key)


class GoodsObjectKeyConstructor(DefaultObjectKeyConstructor):
    update_at = UpdatedAtKeyBit()


class GoodsListKeyConstructor(DefaultListKeyConstructor):
    update_at = UpdatedAtKeyBit()


# class ShopHomeListKeyConstructor(DefaultListKeyConstructor):
#     update_at = HomeUpdatedAtKeyBit()


class ShopObjectKeyConstructor(DefaultObjectKeyConstructor):
    update_at = UpdatedAtKeyBit()
    user = UserKeyBit()


class ShopListKeyConstructor(DefaultListKeyConstructor):
    update_at = UpdatedAtKeyBit()
    user = UserKeyBit()


shop_object_cache_key_func = ShopObjectKeyConstructor()
shop_list_cache_key_func = ShopListKeyConstructor()


def change_updated_at(sender, instance, **kwargs):
    key = f'{instance.__class__.__name__}ViewSet_updated_at'
    cache.set(key, datetime.utcnow())


# def change_home_updated_at(sender, instance, **kwargs):
#     key = 'HomeViewSet_updated_at'
#     cache.set(key, datetime.utcnow())


def delete_image(sender, instance, **kwargs):
    if isinstance(instance, Goods):
        os.remove(instance.goods_front_image.path)
        os.remove(instance.detailed_desc.path)
    elif isinstance(instance, GoodsImage):
        os.remove(instance.image.path)
    elif isinstance(instance, User):
        os.remove(instance.avatar.path)


for model in [User, UserAddress, Goods, ShoppingCart, OrderInfo]:
    post_save.connect(receiver=change_updated_at, sender=model)
    post_delete.connect(receiver=change_updated_at, sender=model)

# for model in [Banner, Goods]:
#     post_save.connect(receiver=change_home_updated_at, sender=model)
#     post_delete.connect(receiver=change_home_updated_at, sender=model)

for model in [Goods, GoodsImage, User]:
    pre_delete.connect(receiver=delete_image, sender=model)

