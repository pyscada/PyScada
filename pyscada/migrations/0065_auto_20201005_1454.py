# Generated by Django 2.2.8 on 2020-10-05 14:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pyscada", "0064_auto_20201005_1443"),
    ]

    operations = [
        migrations.AlterField(
            model_name="complexevent",
            name="complex_mail_recipients",
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="complexeventitem",
            name="custom_validation",
            field=models.CharField(blank=True, default="", max_length=400, null=True),
        ),
    ]
