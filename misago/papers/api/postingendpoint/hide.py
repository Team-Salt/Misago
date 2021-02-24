from rest_framework import serializers

from . import PostingEndpoint, PostingMiddleware
from ... import moderation


class HideMiddleware(PostingMiddleware):
    def use_this_middleware(self):
        return self.mode == PostingEndpoint.START

    def get_serializer(self):
        return HideSerializer(data=self.request.data)

    def post_save(self, serializer):
        if self.paper.category.acl["can_hide_papers"]:
            if serializer.validated_data.get("hide"):
                moderation.hide_paper(self.request, self.paper)
                self.paper.update_all = True
                self.paper.save(update_fields=["is_hidden"])

                self.paper.category.synchronize()
                self.paper.category.update_all = True


class HideSerializer(serializers.Serializer):
    hide = serializers.BooleanField(required=False, default=False)
