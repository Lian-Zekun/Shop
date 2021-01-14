import time

from django.core.files import File
from django.db import transaction
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.users.models import UserAddress

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[
        UniqueValidator(queryset=User.objects.all(), message='用户已经存在')
    ])
    
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar', 'password', 'ctime')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        if validated_data.get('avatar'):
            instance.avatar = validated_data['avatar']
        instance.save()
        return instance


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserAddress
        fields = '__all__'

    def create(self, validated_data):
        instance = super(AddressSerializer, self).create(validated_data)
        if instance.is_default:
            UserAddress.update_default_address(self.user, instance.id)
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        with transaction.atomic():
            if validated_data.get('is_default'):
                UserAddress.update_default_address(self.user, instance.id)
            instance.save()
        return instance
