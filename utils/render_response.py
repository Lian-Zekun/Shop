from rest_framework.renderers import JSONRenderer


class ShopRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # print(data, renderer_context)
        if renderer_context:
            state = 0 if renderer_context['response'].status_code >= 400 else 1
            ret = {
                'state': state,
                'data': data,
            }
            return super(ShopRenderer, self).render(ret, accepted_media_type, renderer_context)
        else:
            return super(ShopRenderer, self).render(data, accepted_media_type, renderer_context)
