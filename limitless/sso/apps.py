from django.apps import AppConfig


class LimitLessSSOConfig(AppConfig):
    """
    Using https://github.com/divio/django-simple-sso
    """

    name = "limitless.sso"
    label = "limitless_sso"
    verbose_name = "LimitLess Single Sign On"
