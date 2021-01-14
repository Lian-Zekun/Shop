from django.contrib import admin

from apps.users.models import UserAddress, User


@admin.register(User)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['username', 'ctime']


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['signer', 'phone', 'address', 'is_default']


admin.site.site_header = 'XMall 商城'
admin.site.site_footer = 'XMall 商城'
admin.site.menu_style = 'accordion'
