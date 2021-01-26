from django.contrib import admin
from django.views.static import serve
from rest_framework.documentation import include_docs_urls

from django.urls import path, re_path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from Shop.settings import MEDIA_ROOT
from rest_framework.routers import SimpleRouter

from apps.goods.views import GoodsViewSet, HomeView, GoodsSearchView
from apps.trade.views import ShoppingCartViewSet, OrderInfoViewSet
from apps.users.views import UserViewSet, UserAddressViewSet

router = SimpleRouter()

# 配置goods的url,这个basename是干啥的
router.register('goods', GoodsViewSet, basename='goods')

# 配置users的url
router.register('user', UserViewSet, basename='user')

# 收货地址
router.register('address', UserAddressViewSet, basename='address')

# 购物车
router.register('carts', ShoppingCartViewSet, basename='carts')

# 订单相关url
router.register('orders', OrderInfoViewSet, basename='orders')

router.register('search', GoodsSearchView, basename='search')

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),

    path('api/', include(router.urls)),
    path('api/home/', HomeView.as_view(), name='home'),
    path('api/login/', obtain_jwt_token),
    path('api/refresh/', refresh_jwt_token),

    path('docs/', include_docs_urls(title='XMall 商城文档')),
]
