import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "FlowerShop.settings")

from random import randint, choice

import django
from django.core.files import File
django.setup()


def main():
    from apps.goods.models import Goods, GoodsImage
    path = 'flower'
    file_names = os.listdir(path)

    for file_name in file_names:
        name = file_name.split(' ')[0]
        brief_desc = file_name.split(' ')[1]
        stock = randint(100, 1000)
        price = randint(100, 1000)
        detailed_desc = File(open(os.path.join(path, file_name, '长图.jpg'), 'rb'), name=f'{name}_detail.jpg')
        goods_front_image = File(open(os.path.join(path, file_name, '1.jpg'), 'rb'), name=f'{name}_1.jpg')
        is_new = choice([True, False])
        is_hot = choice([True, False])
        goods = Goods.objects.create(
            name=name, stock=stock, price=price, brief_desc=brief_desc, detailed_desc=detailed_desc,
            goods_front_image=goods_front_image, is_hot=is_hot, is_new=is_new
        )
        img2 = File(open(os.path.join(path, file_name, '2.jpg'), 'rb'), name=f'{name}_2.jpg')
        img3 = File(open(os.path.join(path, file_name, '3.jpg'), 'rb'), name=f'{name}_3.jpg')
        img4 = File(open(os.path.join(path, file_name, '4.jpg'), 'rb'), name=f'{name}_4.jpg')
        GoodsImage.objects.create(goods=goods, image=img2)
        GoodsImage.objects.create(goods=goods, image=img3)
        GoodsImage.objects.create(goods=goods, image=img4)


if __name__ == '__main__':
    main()
    print('Done!')
