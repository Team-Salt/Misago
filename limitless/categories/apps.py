from django.apps import AppConfig


class LimitLessCategoriesConfig(AppConfig):
    name = "limitless.categories"
    label = "limitless_categories"
    verbose_name = "LimitLess Categories"

    def ready(self):
        from . import signals as _
