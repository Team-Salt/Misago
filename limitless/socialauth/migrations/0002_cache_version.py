from django.db import migrations

from .. import SOCIALAUTH_CACHE
from ...cache.operations import StartCacheVersioning


class Migration(migrations.Migration):

    dependencies = [
        ("limitless_socialauth", "0001_initial"),
        ("limitless_cache", "0001_initial"),
    ]

    operations = [StartCacheVersioning(SOCIALAUTH_CACHE)]
