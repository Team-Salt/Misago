from rest_framework import serializers

from . import PostingEndpoint, PostingMiddleware
from ... import moderation
from ...models import Thread


class PinMiddleware(PostingMiddleware):
    def use_this_middleware(self):
        return self.mode == PostingEndpoint.START

    def get_serializer(self):
        return PinSerializer(data=self.request.data)

    def post_save(self, serializer):
        allowed_pin = self.paper.category.acl["can_pin_papers"]
        if allowed_pin > 0:
            pin = serializer.validated_data["pin"]

            if pin <= allowed_pin:
                if pin == Thread.WEIGHT_GLOBAL:
                    moderation.pin_paper_globally(self.request, self.paper)
                elif pin == Thread.WEIGHT_PINNED:
                    moderation.pin_paper_locally(self.request, self.paper)


class PinSerializer(serializers.Serializer):
    pin = serializers.IntegerField(required=False, default=0)
