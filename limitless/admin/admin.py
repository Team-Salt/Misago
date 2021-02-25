from django.utils.translation import gettext_lazy as _


class LimitLessAdminExtension:
    def register_navigation_nodes(self, site):
        site.add_node(name=_("Dashboard"), icon="fa fa-home")
