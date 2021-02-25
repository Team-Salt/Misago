from debug_toolbar.panels import Panel
from django.utils.translation import gettext_lazy as _


class LimitLessACLPanel(Panel):
    """panel that displays current user's ACL"""

    title = _("LimitLess User ACL")
    template = "limitless/acl_debug.html"

    @property
    def nav_subtitle(self):
        limitless_user = self.get_stats().get("limitless_user")

        if limitless_user and limitless_user.is_authenticated:
            return limitless_user.username
        return _("Anonymous user")

    def process_response(self, request, response):
        try:
            limitless_user = request.user
        except AttributeError:
            limitless_user = None

        try:
            limitless_acl = request.user_acl
        except AttributeError:
            limitless_acl = {}

        self.record_stats({"limitless_user": limitless_user, "limitless_acl": limitless_acl})
