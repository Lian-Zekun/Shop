# Generated by Django 3.1.2 on 2021-01-08 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0003_auto_20201227_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(upload_to='banner/%Y/%m/%d/', verbose_name='轮播图片'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='detailed_desc',
            field=models.ImageField(upload_to='goods/desc/%Y/%m/%d/', verbose_name='商品具体描述'),
        ),
        migrations.AlterField(
            model_name='goods',
            name='goods_front_image',
            field=models.ImageField(upload_to='goods/detail/%Y/%m/%d/', verbose_name='封面图'),
        ),
        migrations.AlterField(
            model_name='goodsimage',
            name='image',
            field=models.ImageField(upload_to='goods/detail/%Y/%m/%d/', verbose_name='图片'),
        ),
    ]