from django.apps import AppConfig


class LimitLessThreadsConfig(AppConfig):
    name = "limitless.threads"
    label = "limitless_threads"
    verbose_name = "LimitLess Threads"

    def ready(self):
        from . import signals as _
