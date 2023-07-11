# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("pyscada", "0014_auto_20160210_1152"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="mail_recipient",
        ),
        migrations.RemoveField(
            model_name="mail",
            name="mail_from",
        ),
        migrations.RemoveField(
            model_name="mail",
            name="mail_recipients",
        ),
        migrations.AddField(
            model_name="event",
            name="mail_recipients",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="mail",
            name="to_email",
            field=models.EmailField(default="root@localhost", max_length=254),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name="MailRecipient",
        ),
    ]
