from django.apps import AppConfig


class LimitLessLegalConfig(AppConfig):
    name = "limitless.legal"
    label = "limitless_legal"
    verbose_name = "LimitLess Legal"

    def ready(self):
        from . import signals as _
