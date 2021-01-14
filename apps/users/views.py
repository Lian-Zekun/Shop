import time

from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins, permissions
from rest_framework import viewsets, status
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler

from apps.users.models import UserAddress
from apps.users.serializers import UserSerializer, AddressSerializer
from utils.permissions import IsOwnerOrReadOnly

User = get_user_model()


class UserViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        payload = jwt_payload_handler(user)
        re_dict = {
            'token': jwt_encode_handler(payload),
            'user': serializer.data
        }

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = self.convert_update_params(request.data)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def convert_update_params(self, data):
        if data.get('old_password') and not self.request.user.check_password(data.get('old_password')):
            raise ValidationError(detail={'old_password': ['原密码错误']})

        if data.get('avatar'):
            img_type = data['avatar'].content_type.split('/')[1]
            data['avatar'] = File(data['avatar'], name=f'{int(round(time.time() * 1000))}.{img_type}')
        return data


class UserAddressViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication,)
    serializer_class = AddressSerializer
    pagination_class = None

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)
