# Generated by Django 4.2.5 on 2023-11-16 16:05

from django.db import migrations, models
import django.db.models.deletion
import pyscada.hmi.models


class Migration(migrations.Migration):
    dependencies = [
        ("hmi", "0075_alter_processflowdiagram_url_height_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DisplayValueOptionTemplate",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=40, unique=True)),
                (
                    "template_name",
                    models.CharField(
                        blank=True,
                        help_text="The template to use for the control item. Must ends with '.html'.",
                        max_length=100,
                        validators=[pyscada.hmi.models.validate_html],
                    ),
                ),
                (
                    "js_files",
                    models.TextField(
                        blank=True,
                        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
                        max_length=400,
                    ),
                ),
                (
                    "css_files",
                    models.TextField(
                        blank=True,
                        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
                        max_length=100,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TransformData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("inline_model_name", models.CharField(max_length=100)),
                ("short_name", models.CharField(max_length=20)),
                ("js_function_name", models.CharField(max_length=100)),
                (
                    "js_files",
                    models.TextField(
                        blank=True,
                        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
                        max_length=100,
                    ),
                ),
                (
                    "css_files",
                    models.TextField(
                        blank=True,
                        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
                        max_length=100,
                    ),
                ),
                (
                    "need_historical_data",
                    models.BooleanField(
                        default=False,
                        help_text="If true, will query the data corresponding of the date range picker.",
                    ),
                ),
            ],
        ),
        migrations.RenameField(
            model_name="displayvalueoption",
            old_name="name",
            new_name="title",
        ),
        migrations.RemoveField(
            model_name="displayvalueoption",
            name="type",
        ),
        migrations.AddField(
            model_name="displayvalueoption",
            name="template",
            field=models.ForeignKey(
                blank=True,
                help_text="Select a custom template to use for this control item display value option.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="hmi.displayvalueoptiontemplate",
            ),
        ),
        migrations.AddField(
            model_name="displayvalueoption",
            name="transform_data",
            field=models.ForeignKey(
                blank=True,
                help_text="Select a function to transform and manipulate data before displaying it.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="hmi.transformdata",
            ),
        ),
    ]
