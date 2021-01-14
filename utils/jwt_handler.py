from apps.users.serializers import UserSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    设置jwt登录之后返回token和user信息
    """
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }
