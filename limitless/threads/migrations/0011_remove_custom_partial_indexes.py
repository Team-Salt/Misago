# Generated by Django 2.2.1 on 2019-05-18 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("limitless_threads", "0010_auto_20180609_1523")]

    operations = [
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_has_ope_479906_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_is_hidd_85db69_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_is_even_42bda7_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_weight_955884_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_weight_9e8f9c_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_weight_c7ef29_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_weight__4af9ee_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_has_rep_84acfa_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_has_una_b0dbf5_part"),
        migrations.RunSQL("DROP INDEX IF EXISTS limitless_thre_is_hidd_d2b96c_part"),
    ]
