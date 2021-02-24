from django.utils.translation import gettext as _

from . import PostingEndpoint, PostingMiddleware
from ....acl import useracl
from ....core.mail import build_mail, send_messages
from ...permissions import can_see_post, can_see_paper


class EmailNotificationMiddleware(PostingMiddleware):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.previous_last_post_on = self.paper.last_post_on

    def use_this_middleware(self):
        return self.mode == PostingEndpoint.REPLY

    def post_save(self, serializer):
        queryset = (
            self.paper.subscription_set.filter(
                send_email=True, last_read_on__gte=self.previous_last_post_on
            )
            .exclude(user=self.user)
            .select_related("user")
        )

        notifications = []
        for subscription in queryset.iterator():
            if self.subscriber_can_see_post(subscription.user):
                notifications.append(self.build_mail(subscription.user))

        if notifications:
            send_messages(notifications)

    def subscriber_can_see_post(self, subscriber):
        user_acl = useracl.get_user_acl(subscriber, self.request.cache_versions)
        see_paper = can_see_paper(user_acl, self.paper)
        see_post = can_see_post(user_acl, self.post)
        return see_paper and see_post

    def build_mail(self, subscriber):
        if subscriber.id == self.paper.starter_id:
            subject = _('%(user)s has replied to your paper "%(paper)s"')
        else:
            subject = _(
                '%(user)s has replied to paper "%(paper)s" that you are watching'
            )

        subject_formats = {"user": self.user.username, "paper": self.paper.title}

        return build_mail(
            subscriber,
            subject % subject_formats,
            "misago/emails/paper/reply",
            sender=self.user,
            context={
                "settings": self.request.settings,
                "paper": self.paper,
                "post": self.post,
            },
        )
