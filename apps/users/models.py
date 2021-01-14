from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, avatar, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        username = self.model.normalize_username(username)
        user = self.model(username=username, avatar=avatar, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, avatar=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, avatar, password, **extra_fields)

    def create_superuser(self, username, avatar=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, avatar, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    avatar = models.ImageField(upload_to='users/', default='users/1.jpeg', verbose_name='头像')
    # email = models.EmailField(max_length=100, null=True, blank=True, verbose_name='邮箱')
    is_active = models.BooleanField(default=True, verbose_name='激活状态')
    is_staff = models.BooleanField(default=False, verbose_name='是否能进入admin界面')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    USERNAME_FIELD = 'username'

    objects = UserManager()

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']
        indexes = [
            models.Index(fields=['username'], name='name_idx')
        ]

    def __str__(self):
        return f'{self.username}-{self.id}'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    address = models.CharField(max_length=256, default='', verbose_name='详细地址')
    signer = models.CharField(max_length=100, default='', verbose_name='签收人')
    phone = models.CharField(max_length=11, default='', verbose_name='电话')
    is_default = models.BooleanField(default=False, verbose_name='是否默认地址')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
        ordering = ['-ctime']

    @staticmethod
    def update_default_address(user, default_address_id):
        queryset = UserAddress.objects.filter(user=user).exclude(pk=default_address_id)
        queryset.update(is_default=False)

    def __str__(self):
        return self.address
