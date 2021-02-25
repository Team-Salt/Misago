from django.db import migrations

_ = lambda s: s


def create_default_categories_roles(apps, schema_editor):
    CategoryRole = apps.get_model("limitless_categories", "CategoryRole")

    CategoryRole.objects.create(
        name=_("In moderation queue"),
        permissions={
            # threads perms
            "limitless.threads.permissions.threads": {
                "require_threads_approval": 1,
                "require_replies_approval": 1,
            }
        },
    )


class Migration(migrations.Migration):

    dependencies = [("limitless_categories", "0005_auto_20170303_2027")]

    operations = [migrations.RunPython(create_default_categories_roles)]
