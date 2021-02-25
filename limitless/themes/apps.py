from django.apps import AppConfig


class LimitLessThemesConfig(AppConfig):
    name = "limitless.themes"
    label = "limitless_themes"
    verbose_name = "LimitLess Theming"

    def ready(self):
        # pylint: disable=unused-import
        from .admin import tasks
