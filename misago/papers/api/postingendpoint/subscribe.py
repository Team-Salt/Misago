from django.contrib.auth import get_user_model

from . import PostingEndpoint, PostingMiddleware
from ...models import Subscription

User = get_user_model()


class SubscribeMiddleware(PostingMiddleware):
    def use_this_middleware(self):
        return self.mode != PostingEndpoint.EDIT

    def post_save(self, serializer):
        self.subscribe_new_paper()
        self.subscribe_replied_paper()

    def subscribe_new_paper(self):
        if self.mode != PostingEndpoint.START:
            return

        if self.user.subscribe_to_started_papers == User.SUBSCRIPTION_NONE:
            return

        self.user.subscription_set.create(
            category=self.paper.category,
            paper=self.paper,
            send_email=self.user.subscribe_to_started_papers == User.SUBSCRIPTION_ALL,
        )

    def subscribe_replied_paper(self):
        if self.mode != PostingEndpoint.REPLY:
            return

        if self.user.subscribe_to_replied_papers == User.SUBSCRIPTION_NONE:
            return

        try:
            return self.user.subscription_set.get(paper=self.paper)
        except Subscription.DoesNotExist:
            pass

        # posts user's posts in this paper, minus events and current post
        posts_queryset = self.user.post_set.filter(
            paper=self.paper, is_event=False
        ).exclude(pk=self.post.pk)

        if posts_queryset.exists():
            return

        self.user.subscription_set.create(
            category=self.paper.category,
            paper=self.paper,
            send_email=self.user.subscribe_to_replied_papers == User.SUBSCRIPTION_ALL,
        )
