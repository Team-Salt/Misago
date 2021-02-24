from django.apps import AppConfig


class MisagoPapersConfig(AppConfig):
    name = "misago.papers"
    label = "misago_papers"
    verbose_name = "Misago Papers"

    def ready(self):
        from . import signals as _
