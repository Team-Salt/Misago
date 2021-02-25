from django.apps import AppConfig

from .providers import providers


class LimitLessACLsConfig(AppConfig):
    name = "limitless.acl"
    label = "limitless_acl"
    verbose_name = "LimitLess ACL framework"

    def ready(self):
        providers.load()
