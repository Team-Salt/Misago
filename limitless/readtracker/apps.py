from django.apps import AppConfig


class LimitLessReadTrackerConfig(AppConfig):
    name = "limitless.readtracker"
    label = "limitless_readtracker"
    verbose_name = "LimitLess Read Tracker"

    def ready(self):
        from . import signals as _
