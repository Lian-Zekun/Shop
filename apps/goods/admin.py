from django.contrib import admin

from apps.goods.models import Goods, GoodsImage, Banner


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    # 显示内容
    list_display = ['name', 'stock', 'price', 'is_new', 'is_hot', 'ctime']
    search_fields = ['name']  # 搜索内容
    list_editable = ['is_hot', 'is_new']  # 列表页可以直接编辑的
    # 分类筛选
    list_filter = ['is_new', 'is_hot', 'ctime']
    list_per_page = 20  # 分页大小
    ordering = ('-ctime',)

    # 在添加商品的时候可以添加商品图片
    class GoodsImagesInline(admin.TabularInline):
        model = GoodsImage
        exclude = ['ctime']

    inlines = [GoodsImagesInline]


@admin.register(Banner)
class BannerGoodsAdmin(admin.ModelAdmin):
    list_display = ['goods', 'image', 'index']
