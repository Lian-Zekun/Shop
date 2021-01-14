from django.db import models


class Goods(models.Model):
    name = models.CharField(max_length=100, verbose_name='商品名')
    stock = models.IntegerField(default=0, verbose_name='库存数')
    price = models.FloatField(default=0, verbose_name='本店价格')
    brief_desc = models.TextField(max_length=500, verbose_name='商品简短描述')
    detailed_desc = models.ImageField(upload_to='goods/desc/%Y/%m/%d/', verbose_name='商品具体描述')
    goods_front_image = models.ImageField(upload_to='goods/detail/%Y/%m/%d/', verbose_name='封面图')
    is_new = models.BooleanField(default=False, verbose_name='是否新品')
    is_hot = models.BooleanField(default=False, verbose_name='是否热销')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']
        indexes = [
            models.Index(fields=['name'], name='goods_name_idx'),
            models.Index(fields=['price'], name='price_idx'),
            models.Index(fields=['is_new'], name='is_new_idx'),
            models.Index(fields=['is_hot'], name='is_hot_idx')
        ]

    def __str__(self):
        return self.name


class GoodsImage(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='images', verbose_name='商品')
    image = models.ImageField(upload_to='goods/detail/%Y/%m/%d/', verbose_name='图片')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '商品轮播'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']

    def __str__(self):
        return self.goods.name


class Banner(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='banner/%Y/%m/%d/', verbose_name='轮播图片')
    index = models.IntegerField(default=0, verbose_name='轮播顺序')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '首页轮播'
        verbose_name_plural = verbose_name
        ordering = ['index']

    def __str__(self):
        return self.goods.name
