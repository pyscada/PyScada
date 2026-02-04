# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable, VariableProperty, Color
from pyscada.utils import (
    _get_objects_for_html as get_objects_for_html,
    get_group_display_permission_list,
)

from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.db import models
from django.contrib.auth.models import Group
from django.template.loader import get_template
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models.query import QuerySet
from django.db.utils import ProgrammingError
from django.conf import settings
from django.forms.models import BaseInlineFormSet

from asgiref.sync import sync_to_async
from datetime import timedelta
from six import text_type
import traceback
from uuid import uuid4
import logging
import json

logger = logging.getLogger(__name__)


def _delete_widget_content(sender, instance, **kwargs):
    """
    delete the widget content instance when a WidgetContentModel is deleted
    """
    if not issubclass(sender, WidgetContentModel):
        return

    # delete WidgetContent Entry
    wcs = WidgetContent.objects.filter(
        content_pk=instance.pk,
        content_model=("%s" % instance.__class__)
        .replace("<class '", "")
        .replace("'>", ""),
    )
    for wc in wcs:
        logger.debug("delete wc %r" % wc)
        wc.delete()


def _create_widget_content(sender, instance, created=False, **kwargs):
    """
    create a widget content instance when a WidgetContentModel is deleted
    """
    if not issubclass(sender, WidgetContentModel):
        return

    # create a WidgetContent Entry
    if created:
        instance.create_widget_content_entry()
    else:
        instance.update_widget_content_entry()
    return


# raise a ValidationError if value not endswith .html or if template not found
def validate_html(value):
    if not value.endswith(".html"):
        raise ValidationError(
            _("%(value)s should ends with '.html'"),
            params={"value": value},
        )
    try:
        get_template(value)
    except TemplateDoesNotExist:
        raise ValidationError(
            _("%(value)s template does not exist."),
            params={"value": value},
        )


# return a list of files from a coma separated string
# if :// not in the file name and the filename is not starting with /, add the static url
def get_js_or_css_set_from_str(self, field):
    result = list()
    if not hasattr(self, field):
        logger.warning(f"{field} not in {self}")
        return result
    files = getattr(self, field)
    for file in files.split(","):
        if file == "":
            continue
        if not file.startswith("/") and "://" not in file:
            STATIC_URL = (
                str(settings.STATIC_URL)
                if hasattr(settings, "STATIC_URL")
                else "/static/"
            )
            result.append(STATIC_URL + file)
        else:
            result.append(file)
    return result


class WidgetContentModel(models.Model):
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super(WidgetContentModel, cls).__init_subclass__(**kwargs)
        models.signals.post_save.connect(_create_widget_content, sender=cls)
        models.signals.pre_delete.connect(_delete_widget_content, sender=cls)

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        logger.info(f"gen_html function of {self} model needs to be overwritten")
        return None, None, {}

    def _get_objects_for_html(
        self, list_to_append=None, obj=None, exclude_model_names=None
    ):
        if obj is None:
            obj = self
        return get_objects_for_html(
            list_to_append=list_to_append,
            obj=obj,
            exclude_model_names=exclude_model_names,
        )

    def add_custom_fields_list(self, opts):
        return opts

    def add_exclude_fields_list(self, opts):
        return opts

    def create_widget_content_entry(self):
        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        wc = WidgetContent(
            content_pk=self.pk, content_model=fullname(self), content_str=self.__str__()
        )
        wc.save()

    def update_widget_content_entry(self):
        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        self.delete_duplicates()
        wc = WidgetContent.objects.get(content_pk=self.pk, content_model=fullname(self))
        wc.content_str = self.__str__()
        wc.save()

    def get_widget_content_entry(self):
        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__

        try:
            return WidgetContent.objects.get(
                content_pk=self.pk,
                content_model=fullname(self),
                content_str=self.__str__(),
            )
        except WidgetContent.DoesNotExist:
            logger.warning(f"Widget content not found for {self}")
            return None

    def delete_duplicates(self):
        for i in WidgetContent.objects.all():
            c = WidgetContent.objects.filter(
                content_pk=i.content_pk, content_model=i.content_model
            ).count()
            if c > 1:
                logger.debug(
                    "%s WidgetContent for %s ( %s )"
                    % (c, i.content_model, i.content_pk)
                )
                for j in range(0, c - 1):
                    WidgetContent.objects.filter(
                        content_pk=i.content_pk, content_model=i.content_model
                    )[j].delete()

    def check_visible_object(self, visible_models_lists):
        visible_model_list_str = f"visible_{self._meta.object_name.lower()}_list"
        if visible_model_list_str in visible_models_lists:
            visible_list = visible_models_lists[visible_model_list_str]
        else:
            return True
        if type(visible_list) == QuerySet and self.pk in visible_list:
            return True
        return False

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        logger.info(f"data_objects function of {self} model should be overwritten")
        return {}

    class Meta:
        abstract = True


class Theme(models.Model):
    name = models.CharField(max_length=400)
    base_filename = models.CharField(
        max_length=400,
        default="base",
        help_text="Enter the filename without '.html'",
    )
    view_filename = models.CharField(
        max_length=400,
        default="view",
        help_text="Enter the filename without '.html'",
    )

    def __str__(self):
        return self.name

    def check_all_themes(self):
        # Delete theme with missing template file
        for theme in Theme.objects.all():
            try:
                get_template(theme.base_filename + ".html")
                get_template(theme.view_filename + ".html")
            except TemplateDoesNotExist as e:
                logger.info(f"Template {e} not found. {self} will be delete.")
                theme.delete()
            else:
                try:
                    get_template(theme.view_filename + ".html").render(
                        {"base_html": theme.base_filename + ".html"}
                    )
                except TemplateDoesNotExist as e:
                    logger.info(
                        f"Template {e} used in the view as base_html not found. {self} will be delete."
                    )
                    theme.delete()
                except TemplateSyntaxError as e:
                    logger.info(e)
                except AttributeError:
                    pass


class ControlElementOption(models.Model):
    name = models.CharField(max_length=400)
    placeholder = models.CharField(max_length=30, default="Enter a value")
    dropdown = models.BooleanField(
        default=False,
        help_text="Show control item as dropdown. The variable must have a dictionary",
    )
    empty_dropdown_value = models.BooleanField(
        default=False,
        help_text="If true, show placeholder as " "default unelectable text",
    )

    def __str__(self):
        return self.name

    def get_js(self):
        files = list()
        return files

    def get_css(self):
        files = list()
        return files

    def get_daterangepicker(self):
        return False

    def get_timeline(self):
        return False


class TransformData(models.Model):
    inline_model_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=20)
    js_function_name = models.CharField(max_length=100)
    js_files = models.TextField(
        max_length=100,
        blank=True,
        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
    )
    css_files = models.TextField(
        max_length=100,
        blank=True,
        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
    )
    need_historical_data = models.BooleanField(
        default=False,
        help_text="If true, will query the data corresponding of the date range picker.",
    )

    def __str__(self):
        return self.short_name

    def get_js(self):
        return get_js_or_css_set_from_str(self, "js_files")

    def get_css(self):
        return get_js_or_css_set_from_str(self, "css_files")


class DisplayValueOptionTemplate(models.Model):
    label = models.CharField(max_length=40, unique=True)
    template_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="The template to use for the control item. Must ends with '.html'.",
        validators=[validate_html],
    )
    js_files = models.TextField(
        max_length=400,
        blank=True,
        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
    )
    css_files = models.TextField(
        max_length=100,
        blank=True,
        help_text="for a file in static, start without /, like : pyscada/js/pyscada/file.js<br>for a local file not in static, start with /, like : /test/file.js<br>for a remote file, indicate the url<br>you can provide a coma separated list",
    )

    def __str__(self):
        return self.label

    def get_js(self):
        return get_js_or_css_set_from_str(self, "js_files")

    def get_css(self):
        return get_js_or_css_set_from_str(self, "css_files")

    # return the template name or template_not_found.html if the template is not found
    def get_template_name(self):
        try:
            validate_html(self.template_name)
            return self.template_name
        except ValidationError as e:
            logger.warning(e)
            return "template_not_found.html"


class DisplayValueOption(models.Model):
    title = models.CharField(max_length=400)
    template = models.ForeignKey(
        DisplayValueOptionTemplate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Select a custom template to use for this control item display value option.",
    )

    color = models.ForeignKey(
        Color,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Default color if no level defined, can be null.<br>"
        "Color < or =< first level, if a level is defined.",
    )
    color_only = models.BooleanField(
        default=False, help_text="If true, will not display the value."
    )
    gradient = models.BooleanField(
        default=False, help_text="Need 1 color option to be defined."
    )
    gradient_higher_level = models.FloatField(
        default=0, help_text="Color defined above will be used for this level."
    )

    timestamp_conversion_choices = (
        (0, "None"),
        (1, "Timestamp in milliseconds to local date"),
        (2, "Timestamp in milliseconds to local time"),
        (3, "Timestamp in milliseconds to local date and time"),
        (4, "Timestamp in seconds to local date"),
        (5, "Timestamp in seconds to local time"),
        (6, "Timestamp in seconds to local date and time"),
    )
    timestamp_conversion = models.PositiveSmallIntegerField(
        default=0, choices=timestamp_conversion_choices
    )

    transform_data = models.ForeignKey(
        TransformData,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Select a function to transform and manipulate data before displaying it.",
    )

    from_timestamp_offset = models.PositiveSmallIntegerField(
        default=None,
        blank=True,
        null=True,
        help_text="Manage the value to be displayed if there is no data within the specified time interval.<br>"
        "If the field is empty, the last known data before the specified time interval will be displayed.<br>"
        "Set a value to add an offset in milliseconds before the start of the specified time interval.",
    )

    def __str__(self):
        return self.title

    def _get_objects_for_html(
        self, list_to_append=None, obj=None, exclude_model_names=None
    ):
        list_to_append = get_objects_for_html(list_to_append, self, exclude_model_names)
        for item in self.displayvaluecoloroption_set.all():
            list_to_append = get_objects_for_html(
                list_to_append, item, ["display_value_option"]
            )
        return list_to_append

    def get_js(self):
        files = list()
        if self.transform_data is not None:
            js_files = self.transform_data.get_js()
            if type(js_files) == list:
                files += js_files
            elif type(js_files) == str:
                files.append(js_files)
        if self.template is not None:
            js_files = self.template.get_js()
            if type(js_files) == list:
                files += js_files
            elif type(js_files) == str:
                files.append(js_files)
        return files

    def get_css(self):
        files = list()
        if self.transform_data is not None:
            css_files = self.transform_data.get_css()
            if type(css_files) == list:
                files += css_files
            elif type(css_files) == str:
                files.append(css_files)
        if self.template is not None:
            css_files = self.template.get_css()
            if type(css_files) == list:
                files += css_files
            elif type(css_files) == str:
                files.append(css_files)
        return files

    def get_daterangepicker(self):
        if self.transform_data is not None:
            return self.transform_data.need_historical_data

    def get_timeline(self):
        if self.transform_data is not None:
            return self.transform_data.need_historical_data


class DisplayValueColorOption(models.Model):
    display_value_option = models.ForeignKey(
        DisplayValueOption, on_delete=models.CASCADE
    )
    color_level = models.FloatField()
    color_level_type_choices = (
        (0, "color =< level"),
        (1, "color < level"),
    )
    color_level_type = models.PositiveSmallIntegerField(
        default=0, choices=color_level_type_choices
    )
    color = models.ForeignKey(
        Color,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Let blank for no color below the selected level.",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["display_value_option", "color_level", "color_level_type"],
                name="unique_display_value_color_option",
            )
        ]
        ordering = ["color_level", "-color_level_type"]


class TransformDataCountValue(models.Model):
    display_value_option = models.OneToOneField(
        DisplayValueOption, on_delete=models.CASCADE
    )
    value = models.FloatField()  # the value to count

    class FormSet(BaseInlineFormSet):
        def clean(self):
            super().clean()
            # get the formset model name, here TransformDataCountValue
            class_name = self.model.__name__
            # check if a transform data has been selected in the admin and if a transform data exist with this id
            if (
                self.data["transform_data"] != ""
                and TransformData.objects.get(id=self.data["transform_data"])
                is not None
            ):
                # get the selected transform data inline model name
                transform_data_name = TransformData.objects.get(
                    id=self.data["transform_data"]
                ).inline_model_name
                # if the selected transform data inline model name is this model, check if the value field has been filled in
                # otherwhise raise a ValidationError
                if (
                    class_name == transform_data_name
                    and self.data[transform_data_name.lower() + "-0-value"] == ""
                    and self.data["transform_data"] != ""
                ):
                    raise ValidationError("Value is required.")


class ControlItem(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default="")
    position = models.PositiveSmallIntegerField(default=0)
    type_choices = (
        (0, "Control Element"),
        (1, "Display Value"),
    )
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices)
    variable = models.ForeignKey(
        Variable, null=True, blank=True, on_delete=models.CASCADE
    )
    variable_property = models.ForeignKey(
        VariableProperty, null=True, blank=True, on_delete=models.CASCADE
    )
    display_value_options = models.ForeignKey(
        DisplayValueOption, null=True, blank=True, on_delete=models.SET_NULL
    )
    control_element_options = models.ForeignKey(
        ControlElementOption, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["position"]

    def __str__(self):
        type_str = ""
        for i in self.type_choices:
            if i[0] == self.type:
                type_str = i[1]

        if self.variable_property:
            return (
                self.id.__str__()
                + "-"
                + type_str.replace(" ", "_")
                + "-"
                + self.label.replace(" ", "_")
                + "-"
                + self.variable_property.name.replace(" ", "_")
            )
        elif self.variable:
            return (
                self.id.__str__()
                + "-"
                + type_str.replace(" ", "_")
                + "-"
                + "-"
                + self.label.replace(" ", "_")
                + "-"
                + "-"
                + self.variable.name.replace(" ", "_")
            )
        else:
            return "Empty control item with id " + self.id.__str__()

    def web_id(self):
        if self.variable_property:
            return (
                "controlitem-"
                + self.id.__str__()
                + "-"
                + self.variable_property.id.__str__()
            )
        elif self.variable:
            return "controlitem-" + self.id.__str__() + "-" + self.variable.id.__str__()

    def web_class_str(self):
        if self.variable_property:
            return "prop-%d" % self.variable_property_id
        elif self.variable:
            return "var-%d" % self.variable_id

    def active(self):
        if self.variable_property:
            return (
                self.variable_property.variable.active
                and self.variable_property.variable.device.active
            )
        elif self.variable:
            return self.variable.active and self.variable.device.active
        return False

    def key(self):
        if self.variable_property:
            return self.variable_property_id
        elif self.variable:
            return self.variable_id

    def name(self):
        if self.variable_property:
            return self.variable_property.name
        elif self.variable:
            return self.variable.name

    def item_type(self):
        if self.variable_property:
            return "variable_property"
        elif self.variable:
            return "variable"

    def unit(self):
        if self.variable_property:
            if self.variable_property.unit is not None:
                return self.variable_property.unit.unit
            else:
                return ""
        elif self.variable:
            return self.variable.unit.unit

    def min(self):
        if self.variable_property:
            return self.variable_property.value_min
        elif self.variable:
            return self.variable.value_min

    def max(self):
        if self.variable_property:
            return self.variable_property.value_max
        elif self.variable:
            return self.variable.value_max

    def value(self):
        if self.variable_property:
            return self.variable_property.value()
        elif self.variable:
            self.variable.query_prev_value()
            return self.variable.prev_value

    def value_class(self):
        if self.variable_property:
            return self.variable_property.value_class
        elif self.variable:
            return self.variable.value_class

    def min_type(self):
        if self.variable_property:
            return self.variable_property.min_type
        elif self.variable:
            return self.variable.min_type

    def max_type(self):
        if self.variable_property:
            return self.variable_property.max_type
        elif self.variable:
            return self.variable.max_type

    def device(self):
        if self.variable_property:
            return self.variable_property.variable.device
        elif self.variable:
            return self.variable.device

    def threshold_values(self):
        tv = dict()
        if (
            self.display_value_options is not None
            and self.display_value_options.color is not None
        ):
            if len(self.display_value_options.displayvaluecoloroption_set.all()) == 0:
                tv["max"] = self.display_value_options.color.color_code()
            else:
                prev_color = self.display_value_options.color
                for (
                    dvco
                ) in self.display_value_options.displayvaluecoloroption_set.all():
                    tv[dvco.color_level] = prev_color.color_code()
                    prev_color = dvco.color
                tv["max"] = prev_color.color_code()
        return json.dumps(tv)

    def gauge_params(self):
        d = dict()
        d["min"] = self.min()
        d["max"] = self.max()
        d["threshold_values"] = self.threshold_values()
        return json.dumps(d)

    def dictionary(self):
        if self.variable_property:
            return self.variable_property.dictionary
        elif self.variable:
            return self.variable.dictionary

    def _get_objects_for_html(
        self, list_to_append=None, obj=None, exclude_model_names=None
    ):
        list_to_append = get_objects_for_html(list_to_append, self, exclude_model_names)
        return list_to_append

    def get_js(self):
        files = list()
        if self.type == 1 and self.display_value_options is not None:
            files += self.display_value_options.get_js()
        if self.type == 0 and self.control_element_options is not None:
            files += self.control_element_options.get_js()
        return files

    def get_css(self):
        files = list()
        if self.type == 1 and self.display_value_options is not None:
            files += self.display_value_options.get_css()
        if self.type == 0 and self.control_element_options is not None:
            files += self.control_element_options.get_css()
        return files

    def get_daterangepicker(self):
        if self.type == 0 and self.control_element_options is not None:
            return self.control_element_options.get_daterangepicker()
        elif self.type == 1 and self.display_value_options is not None:
            return self.display_value_options.get_daterangepicker()
        return False

    def get_timeline(self):
        if self.type == 0 and self.control_element_options is not None:
            return self.control_element_options.get_timeline()
        elif self.type == 1 and self.display_value_options is not None:
            return self.display_value_options.get_timeline()
        return False

    def readable(self):
        if self.variable_property:
            return self.variable_property.variable.readable
        elif self.variable:
            return self.variable.readable


class Chart(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    x_axis_label = models.CharField(max_length=400, default="", blank=True)
    x_axis_var = models.ForeignKey(
        Variable,
        default=None,
        related_name="x_axis_var",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    x_axis_ticks = models.PositiveSmallIntegerField(default=6)
    x_axis_linlog = models.BooleanField(
        default=False, help_text="False->Lin / True->Log"
    )

    def __str__(self):
        return text_type(str(self.id) + ": " + self.title)

    def visible(self):
        return True

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        for axe in self.chartaxis_set.all():
            for item in axe.variables.all():
                if "variable" not in objects:
                    objects["variable"] = []
                objects["variable"].append(item.pk)
        return objects

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs["widget_pk"] if "widget_pk" in kwargs else 0
        widget_extra_css_class = (
            kwargs["widget_extra_css_class"]
            if "widget_extra_css_class" in kwargs
            else ""
        )
        main_template = get_template("chart.html")
        sidebar_template = get_template("chart_legend.html")
        main_content = None
        sidebar_content = None
        if "visible_objects_lists" in kwargs and self.check_visible_object(
            kwargs["visible_objects_lists"]
        ):
            main_content = main_template.render(
                dict(
                    chart=self,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
            sidebar_content = sidebar_template.render(
                dict(
                    chart=self,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
        opts = dict()
        opts["show_daterangepicker"] = True
        opts["show_timeline"] = True
        opts["flot"] = True
        # opts["object_config_list"] = set()
        # opts["object_config_list"].update(self._get_objects_for_html())
        return main_content, sidebar_content, opts

    def _get_objects_for_html(
        self, list_to_append=None, obj=None, exclude_model_names=None
    ):
        list_to_append = super()._get_objects_for_html(
            list_to_append, obj, exclude_model_names
        )
        if obj is None:
            for axis in self.chartaxis_set.all():
                list_to_append = super()._get_objects_for_html(
                    list_to_append, axis, ["chart"]
                )

        return list_to_append


class ChartAxis(models.Model):
    label = models.CharField(max_length=400, default="", blank=True)
    position_choices = (
        (0, "left"),
        (1, "right"),
    )
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    min = models.FloatField(blank=True, null=True)
    max = models.FloatField(blank=True, null=True)
    show_bars = models.BooleanField(default=False, help_text="Show bars")
    show_plot_points = models.BooleanField(
        default=False, help_text="Show the plots points"
    )
    show_plot_lines_choices = (
        (0, "No"),
        (1, "Yes"),
        (2, "Yes as steps"),
    )
    show_plot_lines = models.PositiveSmallIntegerField(
        default=2, help_text="Show the plot lines", choices=show_plot_lines_choices
    )
    stack = models.BooleanField(
        default=False, help_text="Stack all variables of this axis"
    )
    fill = models.BooleanField(
        default=False, help_text="Fill all variables of this axis"
    )
    variables = models.ManyToManyField(Variable)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Y Axis"
        verbose_name_plural = "Y Axis"


class Pie(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    radius = models.PositiveSmallIntegerField(
        default=100, validators=[MaxValueValidator(100), MinValueValidator(1)]
    )
    innerRadius = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    variables = models.ManyToManyField(Variable, blank=True)
    variable_properties = models.ManyToManyField(VariableProperty, blank=True)

    def __str__(self):
        return text_type(str(self.id) + ": " + self.title)

    def visible(self):
        return True

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        for item in self.variables.all():
            if "variable" not in objects:
                objects["variable"] = []
            objects["variable"].append(item.pk)
        for item in self.variable_properties.all():
            if "variable_property" not in objects:
                objects["variable_property"] = []
            objects["variable_property"].append(item.pk)
        return objects

    def gen_html(self, **kwargs):
        """
        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs["widget_pk"] if "widget_pk" in kwargs else 0
        widget_extra_css_class = (
            kwargs["widget_extra_css_class"]
            if "widget_extra_css_class" in kwargs
            else ""
        )
        main_template = get_template("pie.html")
        sidebar_template = get_template("chart_legend.html")
        main_content = None
        sidebar_content = None
        if "visible_objects_lists" in kwargs and self.check_visible_object(
            kwargs["visible_objects_lists"]
        ):
            main_content = main_template.render(
                dict(
                    pie=self,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
            sidebar_content = sidebar_template.render(
                dict(
                    chart=self,
                    pie=1,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
        opts = dict()
        opts["flot"] = True
        opts["topbar"] = True
        return main_content, sidebar_content, opts


class Form(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    button = models.CharField(max_length=50, default="Ok")
    control_items = models.ManyToManyField(
        ControlItem,
        related_name="control_items_form",
        limit_choices_to={"type": "0"},
        blank=True,
    )
    hidden_control_items_to_true = models.ManyToManyField(
        ControlItem,
        related_name="hidden_control_items_form",
        limit_choices_to={"type": "0"},
        blank=True,
    )

    def __str__(self):
        return text_type(str(self.id) + ": " + self.title)

    def visible(self):
        return True

    def web_id(self):
        return "form-" + self.id.__str__()

    def control_items_list(self):
        return [item.pk for item in self.control_items]

    def hidden_control_items_to_true_list(self):
        return [item.pk for item in self.hidden_control_items_to_true]

    def get_js(self):
        files = list()
        for item in self.control_items.all():
            files += item.get_js()
        for item in self.hidden_control_items_to_true.all():
            files += item.get_js()
        return files

    def get_css(self):
        files = list()
        for item in self.control_items.all():
            files += item.get_css()
        for item in self.hidden_control_items_to_true.all():
            files += item.get_css()
        return files

    def get_daterangepicker(self):
        get_daterangepicker = False
        for item in self.control_items.all():
            get_daterangepicker = get_daterangepicker or item.get_daterangepicker()
        for item in self.hidden_control_items_to_true.all():
            get_daterangepicker = get_daterangepicker or item.get_daterangepicker()
        return get_daterangepicker

    def get_timeline(self):
        get_timeline = False
        for item in self.control_items.all():
            get_timeline = get_timeline or item.get_timeline()
        for item in self.hidden_control_items_to_true.all():
            get_timeline = get_timeline or item.get_timeline()
        return get_timeline


class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    link_title = models.SlugField(max_length=80, default="")
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.link_title.replace(" ", "_")

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        groups = user.groups.all() if user is not None else []
        authenticated = True if user is not None else False
        for w in get_group_display_permission_list(
            self.widget_set.filter(visible=True), groups, authenticated
        ):
            wdo = w.data_objects(user)
            for o in wdo.keys():
                if o not in objects:
                    objects[o] = []
                objects[o] = list(set(objects[o] + wdo.get(o, [])))
        return objects


class ControlPanel(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    items = models.ManyToManyField(ControlItem, blank=True)
    forms = models.ManyToManyField(Form, blank=True)

    def __str__(self):
        return str(self.id) + ": " + self.title

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        groups = user.groups.all() if user is not None else []
        authenticated = True if user is not None else False
        for ci in get_group_display_permission_list(
            self.items.all(), groups, authenticated
        ):
            if ci.item_type() not in objects:
                objects[ci.item_type()] = []
            objects[ci.item_type()].append(ci.key())
            if ci.type == 0:
                # accessible in writing
                if f"{ci.item_type()}_write" not in objects:
                    objects[f"{ci.item_type()}_write"] = []
                objects[f"{ci.item_type()}_write"].append(ci.key())
        for form in get_group_display_permission_list(
            self.forms.all(), groups, authenticated
        ):
            for ci in get_group_display_permission_list(
                form.control_items.all(), groups, authenticated
            ):
                if ci.item_type() not in objects:
                    objects[ci.item_type()] = []
                objects[ci.item_type()].append(ci.key())
                if ci.type == 0:
                    # accessible in writing
                    if f"{ci.item_type()}_write" not in objects:
                        objects[f"{ci.item_type()}_write"] = []
                    objects[f"{ci.item_type()}_write"].append(ci.key())
            for ci in get_group_display_permission_list(
                form.hidden_control_items_to_true.all(), groups, authenticated
            ):
                if ci.item_type() not in objects:
                    objects[ci.item_type()] = []
                objects[ci.item_type()].append(ci.key())
                if ci.type == 0:
                    # accessible in writing
                    if f"{ci.item_type()}_write" not in objects:
                        objects[f"{ci.item_type()}_write"] = []
                    objects[f"{ci.item_type()}_write"].append(ci.key())
        return objects

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs["widget_pk"] if "widget_pk" in kwargs else 0
        widget_extra_css_class = (
            kwargs["widget_extra_css_class"]
            if "widget_extra_css_class" in kwargs
            else ""
        )
        main_template = get_template("control_panel.html")
        main_content = None
        if "visible_objects_lists" in kwargs and self.check_visible_object(
            kwargs["visible_objects_lists"]
        ):
            visible_element_list = (
                kwargs["visible_objects_lists"]["visible_controlitem_list"]
                if "visible_controlitem_list" in kwargs["visible_objects_lists"]
                else []
            )
            visible_form_list = (
                kwargs["visible_objects_lists"]["visible_form_list"]
                if "visible_form_list" in kwargs["visible_objects_lists"]
                else []
            )
            main_content = main_template.render(
                dict(
                    control_panel=self,
                    visible_control_element_list=visible_element_list,
                    visible_form_list=visible_form_list,
                    uuid=uuid4().hex,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
        sidebar_content = None
        opts = dict()
        opts["flot"] = False
        opts["javascript_files_list"] = list()
        opts["css_files_list"] = list()
        opts["show_daterangepicker"] = False
        opts["show_timeline"] = False
        for item in self.items.all():
            opts["javascript_files_list"] += item.get_js()
            opts["css_files_list"] += item.get_css()
            opts["show_daterangepicker"] = (
                opts["show_daterangepicker"] or item.get_daterangepicker()
            )
            opts["show_timeline"] = opts["show_timeline"] or item.get_timeline()
        for form in self.forms.all():
            opts["javascript_files_list"] += form.get_js()
            opts["css_files_list"] += form.get_css()
            opts["show_daterangepicker"] = (
                opts["show_daterangepicker"] or form.get_daterangepicker()
            )
            opts["show_timeline"] = opts["show_timeline"] or form.get_timeline()
        # opts["object_config_list"] = set()
        # opts["object_config_list"].update(self._get_objects_for_html())
        # opts = self.add_custom_fields_list(opts)
        return main_content, sidebar_content, opts

    def add_custom_fields_list(self, opts):
        if type(opts) == dict:
            if "custom_fields_list" not in opts:
                opts["custom_fields_list"] = dict()
            opts["custom_fields_list"]["variable"] = [
                {"name": "refresh-requested-timestamp", "value": ""},
                {"name": "value-timestamp", "value": ""},
            ]
            opts["custom_fields_list"]["variableproperty"] = [
                {"name": "refresh-requested-timestamp", "value": ""},
                {"name": "value-timestamp", "value": ""},
            ]
        return opts


class CustomHTMLPanel(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="", blank=True)
    html = models.TextField()
    variables = models.ManyToManyField(Variable, blank=True)
    variable_properties = models.ManyToManyField(VariableProperty, blank=True)

    def __str__(self):
        return str(self.id) + ": " + self.title

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        for variable in self.variables.all():
            if "variable" not in objects:
                objects["variable"] = []
            objects["variable"].append(variable.pk)
        for variable_property in self.variable_properties.all():
            if "variable_property" not in objects:
                objects["variable_property"] = []
            objects["variable_property"].append(variable_property.pk)
        return objects

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs["widget_pk"] if "widget_pk" in kwargs else 0
        widget_extra_css_class = (
            kwargs["widget_extra_css_class"]
            if "widget_extra_css_class" in kwargs
            else ""
        )
        main_template = get_template("custom_html_panel.html")
        main_content = None
        if "visible_objects_lists" in kwargs and self.check_visible_object(
            kwargs["visible_objects_lists"]
        ):
            main_content = main_template.render(
                dict(
                    custom_html_panel=self,
                    widget_pk=widget_pk,
                    widget_extra_css_class=widget_extra_css_class,
                )
            )
        sidebar_content = None
        opts = dict()
        # opts["object_config_list"] = set()
        # opts["object_config_list"].update(self._get_objects_for_html())
        return main_content, sidebar_content, opts


class ProcessFlowDiagramItem(models.Model):
    id = models.AutoField(primary_key=True)
    control_item = models.ForeignKey(
        ControlItem, default=None, blank=True, null=True, on_delete=models.CASCADE
    )
    top = models.PositiveIntegerField(blank=True, default=0)
    left = models.PositiveIntegerField(blank=True, default=0)
    font_size = models.PositiveSmallIntegerField(default=14)
    width = models.PositiveIntegerField(blank=True, default=0)
    height = models.PositiveIntegerField(blank=True, default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        if self.control_item:
            if self.control_item.label != "":
                return str(self.id) + ": " + self.control_item.label
            else:
                return str(self.id) + ": " + self.control_item.name
        else:
            return str(self.id)


class ProcessFlowDiagram(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="", blank=True)
    background_image = models.ImageField(
        upload_to="img/",
        height_field="url_height",
        width_field="url_width",
        verbose_name="background image",
        blank=True,
    )
    type_choices = (
        (0, "HTML"),
        (1, "SVG"),
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=type_choices,
        help_text="HTML is not responsive and can display control element<br>"
        "SVG is responsive and cannot display control element",
    )
    process_flow_diagram_items = models.ManyToManyField(
        ProcessFlowDiagramItem, blank=True
    )
    url_height = models.PositiveIntegerField(editable=False, default="100", null=True)
    url_width = models.PositiveIntegerField(editable=False, default="100", null=True)

    def __str__(self):
        if self.title:
            return str(self.id) + ": " + self.title
        else:
            return str(self.id) + ": " + self.background_image.name

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        groups = user.groups.all() if user is not None else []
        authenticated = True if user is not None else False
        for pfdi in self.process_flow_diagram_items.all():
            if (
                pfdi.control_item is not None
                and pfdi.visible
                and pfdi.control_item
                in get_group_display_permission_list(
                    ControlItem.objects.all(), groups, authenticated
                )
            ):
                if pfdi.control_item.item_type() not in objects:
                    objects[pfdi.control_item.item_type()] = []
                objects[pfdi.control_item.item_type()].append(pfdi.control_item.key())
                if pfdi.control_item.type == 0:
                    # accessible in writing
                    if f"{pfdi.control_item.item_type()}_write" not in objects:
                        objects[f"{pfdi.control_item.item_type()}_write"] = []
                    objects[f"{pfdi.control_item.item_type()}_write"].append(
                        pfdi.control_item.key()
                    )
        return objects

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        main_template = get_template("process_flow_diagram.html")
        try:
            widget_pk = kwargs["widget_pk"] if "widget_pk" in kwargs else 0
            widget_extra_css_class = (
                kwargs["widget_extra_css_class"]
                if "widget_extra_css_class" in kwargs
                else ""
            )
            main_content = None
            if "visible_objects_lists" in kwargs and self.check_visible_object(
                kwargs["visible_objects_lists"]
            ):
                main_content = main_template.render(
                    dict(
                        process_flow_diagram=self,
                        height_width_ratio=100
                        * float(self.url_height)
                        / float(self.url_width),
                        uuid=uuid4().hex,
                        widget_pk=widget_pk,
                        widget_extra_css_class=widget_extra_css_class,
                    )
                )
        except ValueError:
            logger.info(f"ProcessFlowDiagram {self} has no background image defined")
        except FileNotFoundError as e:
            logger.info(f"ProcessFlowDiagram {self} : {e}")
        sidebar_content = None
        opts = dict()
        # opts["object_config_list"] = set()
        # opts["object_config_list"].update(self._get_objects_for_html())

        return main_content, sidebar_content, opts


class SlidingPanelMenu(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    position_choices = ((0, "Control Menu"), (1, "left"), (2, "right"))
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    control_panel = models.ForeignKey(
        ControlPanel, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        if self.control_panel is not None:
            return self.control_panel.data_objects(user)
        return {}


class WidgetContent(models.Model):
    content_model = models.CharField(max_length=400)
    content_pk = models.PositiveIntegerField()
    content_str = models.CharField(default="", max_length=400)

    def create_panel_html(self, **kwargs):
        """
        return main_content, sidebar_content, optional list
        """
        content_model = self._import_content_model()
        try:
            if content_model is not None:
                return content_model.gen_html(**kwargs)
            else:
                logger.info(
                    f"WidgetContent content_model of {self.content_str} is None"
                )
                return "", "", ""
        except:
            logger.error(f"{content_model} unhandled exception", exc_info=True)
            # todo del self
            return "", "", ""

    def get_hidden_config2(self, **kwargs):
        """
        return main_content, sidebar_content, optional list
        """
        content_model = self._import_content_model()
        opts = dict()
        opts["object_config_list"] = set()
        try:
            if content_model is not None:
                opts["object_config_list"].update(content_model._get_objects_for_html())
                opts = content_model.add_custom_fields_list(opts)
                opts = content_model.add_exclude_fields_list(opts)
            else:
                logger.info(
                    f"WidgetContent content_model of {self.content_str} is None"
                )
        except:
            logger.error(f"{content_model} unhandled exception", exc_info=True)
            # todo del self

        return opts

    def _import_content_model(self):
        content_class_str = self.content_model
        class_name = content_class_str.split(".")[-1]
        class_path = content_class_str.replace("." + class_name, "")
        try:
            mod = __import__(class_path, fromlist=[class_name.__str__()])
            content_class = getattr(mod, class_name.__str__())
            if isinstance(content_class, models.base.ModelBase):
                return content_class.objects.get(pk=self.content_pk)
        except ModuleNotFoundError:
            logger.info(
                f"{class_name} of {class_path} not found. A module is not installed ?"
            )
        except ProgrammingError as e:
            logger.info(
                f"{e} A module is not installed ?"
            )
        except:
            logger.error(f"{class_path} unhandled exception", exc_info=True)
        return None

    def __str__(self):
        return "%s [%d] %s" % (
            self.content_model.split(".")[-1],
            self.content_pk,
            self.content_str,
        )  # todo add more infos


class CssClass(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    css_class = models.CharField(max_length=250, default="")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Css Classes"


class Widget(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="", blank=True)
    page = models.ForeignKey(
        Page, null=True, default=None, blank=True, on_delete=models.SET_NULL
    )
    row_choices = (
        (0, "1. row"),
        (1, "2. row"),
        (2, "3. row"),
        (3, "4. row"),
        (4, "5. row"),
        (5, "6. row"),
        (6, "7. row"),
        (7, "8. row"),
        (8, "9. row"),
        (9, "10. row"),
        (10, "11. row"),
        (11, "12. row"),
    )
    row = models.PositiveSmallIntegerField(default=0, choices=row_choices)
    col_choices = ((0, "1. col"), (1, "2. col"), (2, "3. col"), (3, "4. col"))
    col = models.PositiveSmallIntegerField(default=0, choices=col_choices)
    size_choices = (
        (4, "page width"),
        (3, "3/4 page width"),
        (2, "1/2 page width"),
        (1, "1/4 page width"),
    )
    size = models.PositiveSmallIntegerField(default=4, choices=size_choices)
    visible = models.BooleanField(default=True)
    content = models.ForeignKey(
        WidgetContent, null=True, default=None, on_delete=models.SET_NULL
    )
    extra_css_class = models.ForeignKey(
        CssClass, null=True, default=None, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ["row", "col"]

    def __str__(self):
        if self.title is not None and self.page:
            return str(self.id) + ": " + self.page.title + ", " + self.title
        else:
            return str(self.id) + ": " + "None, None"

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        if self.content is not None:
            content_model = self.content._import_content_model()
            groups = user.groups.all() if user is not None else []
            authenticated = True if user is not None else False
            if (
                content_model is not None
                and hasattr(content_model, "data_objects")
                and (
                    not hasattr(content_model, "groupdisplaypermission")
                    or content_model
                    in get_group_display_permission_list(
                        content_model.__class__.objects.all(), groups, authenticated
                    )
                )
            ):
                return content_model.data_objects(user)
        return {}

    def css_class(self):
        widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-12"
        widgets = Widget.objects.filter(
            visible=True, page=self.page, row=self.row, content__isnull=False
        )
        if self.size == 3:
            if self.col in [1, 2, 3] and len(widgets.filter(col=0)) == 0:
                # no widget on same row and column 0: offset 3 on lg
                widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-9 col-lg-offset-3"
            else:
                widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-9"
        elif self.size == 2:
            if self.col == 1 and len(widgets.filter(col=0)) == 0:
                widget_size = "col-xs-12 col-sm-12 col-md-6 col-md-offset-3 col-lg-6 col-lg-offset-3"
            elif self.col in [2, 3] and len(widgets.filter(col__in=[0, 1])) == 0:
                widget_size = "col-xs-12 col-sm-12 col-md-6 col-md-offset-6 col-lg-6 col-lg-offset-6"
            else:
                widget_size = "col-xs-12 col-sm-12 col-md-6 col-lg-6"
        elif self.size == 1:
            if self.col == 1 and len(widgets.filter(col=0)) == 0:
                widget_size = "col-xs-12 col-sm-6 col-md-6 col-lg-3 col-lg-offset-3"
            elif self.col == 2 and len(widgets.filter(col__in=[0, 1])) == 0:
                widget_size = "col-xs-12 col-sm-6 col-sm-offset-6 col-md-6 col-md-offset-6 col-lg-3 col-lg-offset-6"
            elif self.col == 3 and len(widgets.filter(col__in=[0, 1, 2])) == 0:
                widget_size = "col-xs-12 col-sm-6 col-sm-offset-6 col-md-6 col-md-offset-6 col-lg-3 col-lg-offset-9"
            else:
                widget_size = "col-xs-12 col-sm-6 col-md-6 col-lg-3"
        return (
            "widget_row_"
            + str(self.row)
            + " widget_col_"
            + str(self.col)
            + " "
            + widget_size
        )


class View(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    description = models.TextField(default="", verbose_name="Description", null=True)
    link_title = models.SlugField(max_length=80, default="")
    pages = models.ManyToManyField(Page)
    sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu, blank=True)
    logo = models.ImageField(
        upload_to="img/", verbose_name="Overview Picture", blank=True
    )
    visible = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)
    show_timeline = models.BooleanField(default=True)
    theme = models.ForeignKey(
        Theme, blank=True, null=True, default=None, on_delete=models.SET_NULL
    )
    default_time_delta = models.DurationField(default=timedelta(hours=2))

    def __str__(self):
        return self.title

    def data_objects(self, user):
        # used to get all objects which need to retrive data
        objects = {}
        if self.visible:
            groups = user.groups.all() if user is not None else []
            authenticated = True if user is not None else False
            for w in get_group_display_permission_list(
                self.sliding_panel_menus.all(), groups, authenticated
            ):
                wdo = w.data_objects(user)
                for o in wdo.keys():
                    if o not in objects:
                        objects[o] = []
                    objects[o] = list(set(objects[o] + wdo.get(o, [])))
            for w in get_group_display_permission_list(
                self.pages.all(), groups, authenticated
            ):
                wdo = w.data_objects(user)
                for o in wdo.keys():
                    if o not in objects:
                        objects[o] = []
                    objects[o] = list(set(objects[o] + wdo.get(o, [])))
        return objects

    class Meta:
        ordering = ["position"]

class ExternalView(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default="")
    description = models.TextField(default="", verbose_name="Description", null=True)
    url = models.URLField()
    logo = models.ImageField(
        upload_to="img/", verbose_name="Overview Picture", blank=True
    )
    visible = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["position"]


class GroupDisplayPermission(models.Model):
    hmi_group = models.OneToOneField(
        Group, blank=True, null=True, on_delete=models.CASCADE
    )
    unauthenticated_users = models.BooleanField(default=False)
    type_choices = (
        (0, "allow"),
        (1, "exclude"),
    )

    def __str__(self):
        if self.hmi_group is not None:
            return self.hmi_group.name
        elif not self.unauthenticated_users:
            return "Users without any group"
        else:
            return "Unauthenticated users"


class PieGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    pies = models.ManyToManyField(
        Pie, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = Pie

    def __str__(self):
        return str(self.group_display_permission)


class PageGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    pages = models.ManyToManyField(
        Page, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = Page

    def __str__(self):
        return str(self.group_display_permission)


class SlidingPanelMenuGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    sliding_panel_menus = models.ManyToManyField(
        SlidingPanelMenu, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = SlidingPanelMenu

    def __str__(self):
        return str(self.group_display_permission)


class ChartGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    charts = models.ManyToManyField(
        Chart, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = Chart

    def __str__(self):
        return str(self.group_display_permission)


class ControlItemGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    control_items = models.ManyToManyField(
        ControlItem, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = ControlItem

    def __str__(self):
        return str(self.group_display_permission)


class FormGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    forms = models.ManyToManyField(
        Form, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = Form

    def __str__(self):
        return str(self.group_display_permission)


class WidgetGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    widgets = models.ManyToManyField(
        Widget, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = Widget

    def __str__(self):
        return str(self.group_display_permission)


class CustomHTMLPanelGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    custom_html_panels = models.ManyToManyField(
        CustomHTMLPanel, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = CustomHTMLPanel

    def __str__(self):
        return str(self.group_display_permission)


class ViewGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    views = models.ManyToManyField(
        View, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = View

    def __str__(self):
        return str(self.group_display_permission)


class ProcessFlowDiagramGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(
        GroupDisplayPermission, null=True, on_delete=models.CASCADE
    )
    type = models.PositiveSmallIntegerField(
        default=0,
        choices=GroupDisplayPermission.type_choices,
        help_text="If allow: only selected items can be seen by the group."
        "<br>If exclude: allows all items except the selected ones.",
    )
    process_flow_diagram = models.ManyToManyField(
        ProcessFlowDiagram, blank=True, related_name="groupdisplaypermission"
    )
    m2m_related_model = ProcessFlowDiagram

    def __str__(self):
        return str(self.group_display_permission)
