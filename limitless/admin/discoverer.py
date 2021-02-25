from importlib import import_module

from django.apps import apps

from .site import site
from .urlpatterns import urlpatterns


def discover_limitless_admin():
    for app in apps.get_app_configs():
        module = import_module(app.name)
        if not hasattr(module, "admin"):
            continue

        admin_module = import_module("%s.admin" % app.name)
        if hasattr(admin_module, "LimitLessAdminExtension"):
            extension = getattr(admin_module, "LimitLessAdminExtension")()
            if hasattr(extension, "register_navigation_nodes"):
                extension.register_navigation_nodes(site)
            if hasattr(extension, "register_urlpatterns"):
                extension.register_urlpatterns(urlpatterns)
