# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, Variable, VariableProperty, Color
from pyscada.utils import _get_objects_for_html as get_objects_for_html

from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.db import models
from django.contrib.auth.models import Group
from django.template.loader import get_template
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
        content_model=('%s' % instance.__class__).replace("<class '", '').replace("'>", ''))
    for wc in wcs:
        logger.debug('delete wc %r' % wc)
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


def validate_tempalte(value):
    try:
        get_template(value + '.html').render()
    except TemplateDoesNotExist:
        logger.warning("Template filename not found.")
        raise ValidationError(
            _("Template filename not found."),
        )
    except TemplateSyntaxError:
        pass


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
        return '', '', ''

    def _get_objects_for_html(self, list_to_append=None, obj=None, exclude_model_names=None):
        if obj is None:
            obj = self
        return get_objects_for_html(list_to_append=list_to_append, obj=obj, exclude_model_names=exclude_model_names)

    def create_widget_content_entry(self):
        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__
        wc = WidgetContent(content_pk=self.pk,
                           content_model=fullname(self),
                           content_str=self.__str__())
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
            return WidgetContent.objects.get(content_pk=self.pk,
                          content_model=fullname(self),
                          content_str=self.__str__())
        except WidgetContent.DoesNotExist:
            logger.warning(f'Widget content not found for {self}')
            return None

    def delete_duplicates(self):
        for i in WidgetContent.objects.all():
            c = WidgetContent.objects.filter(content_pk=i.content_pk, content_model=i.content_model).count()
            if c > 1:
                logger.debug("%s WidgetContent for %s ( %s )" % (c, i.content_model, i.content_pk))
                for j in range(0, c-1):
                    WidgetContent.objects.filter(content_pk=i.content_pk, content_model=i.content_model)[j].delete()

    class Meta:
        abstract = True


class Theme(models.Model):
    name = models.CharField(max_length=400)
    base_filename = models.CharField(max_length=400, default='base', help_text="Enter the filename without '.html'",
                                     validators=[validate_tempalte])
    view_filename = models.CharField(max_length=400, default='view', help_text="Enter the filename without '.html'",
                                     validators=[validate_tempalte])

    def __str__(self):
        return self.name

    def check_all_themes(self):
        # Delete theme with missing template file
        for theme in Theme.objects.all():
            try:
                get_template(theme.view_filename + '.html').render()
                get_template(theme.base_filename + '.html').render()
            except TemplateDoesNotExist:
                theme.delete()
            except TemplateSyntaxError:
                pass


class ControlElementOption(models.Model):
    name = models.CharField(max_length=400)
    placeholder = models.CharField(max_length=30, default='Enter a value')
    dropdown = models.BooleanField(default=False,
                                   help_text="Show control item as dropdown. The variable must have a dictionary")
    empty_dropdown_value = models.BooleanField(default=False, help_text='If true, show placeholder as '
                                                                        'default unelectable text')

    def __str__(self):
        return self.name


class DisplayValueOption(models.Model):
    name = models.CharField(max_length=400)
    type_choices = (
        (0, 'Classic (Div)'),
        (1, 'Horizontal gauge'),
        (2, 'Vertical gauge'),
        (3, 'Circular gauge'),
    )
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices)

    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.CASCADE,
                              help_text="Default color if no level defined, can be null.<br>"
                                        "Color < or =< first level, if a level is defined.")
    color_only = models.BooleanField(default=False, help_text="If true, will not display the value.")
    gradient = models.BooleanField(default=False, help_text="Need 1 color option to be defined.")
    gradient_higher_level = models.FloatField(default=0,
                                              help_text="Color defined above will be used for this level.")

    timestamp_conversion_choices = (
        (0, 'None'),
        (1, 'Timestamp in milliseconds to local date'),
        (2, 'Timestamp in milliseconds to local time'),
        (3, 'Timestamp in milliseconds to local date and time'),
        (4, 'Timestamp in seconds to local date'),
        (5, 'Timestamp in seconds to local time'),
        (6, 'Timestamp in seconds to local date and time'),)
    timestamp_conversion = models.PositiveSmallIntegerField(default=0,
                                                            choices=timestamp_conversion_choices)

    def __str__(self):
        return self.name

    def _get_objects_for_html(self, list_to_append=None, obj=None, exclude_model_names=None):
        list_to_append = get_objects_for_html(list_to_append, self, exclude_model_names)
        for item in self.displayvaluecoloroption_set.all():
            list_to_append = get_objects_for_html(list_to_append, item, ['display_value_option'])
        return list_to_append


class DisplayValueColorOption(models.Model):
    display_value_option = models.ForeignKey(DisplayValueOption, on_delete=models.CASCADE)
    color_level = models.FloatField()
    color_level_type_choices = (
        (0, 'color =< level'),
        (1, 'color < level'),)
    color_level_type = models.PositiveSmallIntegerField(default=0, choices=color_level_type_choices)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.CASCADE,
                              help_text="Let blank for no color below the selected level.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['display_value_option', 'color_level', 'color_level_type'],
                                    name='unique_display_value_color_option')
        ]
        ordering = ['color_level', '-color_level_type']


class ControlItem(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default='')
    position = models.PositiveSmallIntegerField(default=0)
    type_choices = (
        (0, 'Control Element'),
        (1, 'Display Value'),
    )
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices)
    variable = models.ForeignKey(Variable, null=True, blank=True, on_delete=models.CASCADE)
    variable_property = models.ForeignKey(VariableProperty, null=True, blank=True, on_delete=models.CASCADE)
    display_value_options = models.ForeignKey(DisplayValueOption, null=True, blank=True, on_delete=models.SET_NULL)
    control_element_options = models.ForeignKey(ControlElementOption, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['position']

    def __str__(self):
        type_str = ""
        for i in self.type_choices:
            if i[0] == self.type:
                type_str = i[1]

        if self.variable_property:
            return self.id.__str__() + "-" + type_str.replace(' ', '_') + "-" + self.label.replace(' ', '_') + "-" + \
                   self.variable_property.name.replace(' ', '_')
        elif self.variable:
            return self.id.__str__() + "-" + type_str.replace(' ', '_') + "-" + "-" + self.label.replace(' ', '_') + "-" + "-" + \
                   self.variable.name.replace(' ', '_')
        else:
            return "Empty control item with id " + self.id.__str__()

    def web_id(self):
        if self.variable_property:
            return "controlitem-" + self.id.__str__() + "-" + self.variable_property.id.__str__()
        elif self.variable:
            return "controlitem-" + self.id.__str__() + "-" + self.variable.id.__str__()

    def web_class_str(self):
        if self.variable_property:
            return 'prop-%d' % self.variable_property_id
        elif self.variable:
            return 'var-%d' % self.variable_id

    def active(self):
        if self.variable_property:
            return self.variable_property.variable.active and self.variable_property.variable.device.active
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
                return ''
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
            self.variable.query_prev_value(0)
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
        if self.display_value_options is not None and self.display_value_options.color is not None:
            if len(self.display_value_options.displayvaluecoloroption_set.all()) == 0:
                tv["max"] = self.display_value_options.color.color_code()
            else:
                prev_color = self.display_value_options.color
                for dvco in self.display_value_options.displayvaluecoloroption_set.all():
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

    def _get_objects_for_html(self, list_to_append=None, obj=None, exclude_model_names=None):
        list_to_append = get_objects_for_html(list_to_append, self, exclude_model_names)
        return list_to_append


class Chart(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    x_axis_label = models.CharField(max_length=400, default='', blank=True)
    x_axis_var = models.ForeignKey(Variable, default=None, related_name='x_axis_var', null=True, blank=True,
                                   on_delete=models.SET_NULL)
    x_axis_ticks = models.PositiveSmallIntegerField(default=6)
    x_axis_linlog = models.BooleanField(default=False, help_text="False->Lin / True->Log")

    def __str__(self):
        return text_type(str(self.id) + ': ' + self.title)

    def visible(self):
        return True

    def variables_list(self, exclude_list=[]):
        list = []
        for axe in self.chart_set.all():
            for item in axe.variables.exclude(pk__in=exclude_list):
                list.append(item)
        return list

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs['widget_pk'] if 'widget_pk' in kwargs else 0
        widget_extra_css_class = kwargs["widget_extra_css_class"] if "widget_extra_css_class" in kwargs else ""
        main_template = get_template('chart.html')
        sidebar_template = get_template('chart_legend.html')
        main_content = main_template.render(dict(chart=self, widget_pk=widget_pk, widget_extra_css_class=widget_extra_css_class,))
        sidebar_content = sidebar_template.render(dict(chart=self, widget_pk=widget_pk, widget_extra_css_class=widget_extra_css_class,))
        opts = dict()
        opts['show_daterangepicker'] = True
        opts['show_timeline'] = True
        opts['flot'] = True
        opts["object_config_list"] = set()
        opts["object_config_list"].update(self._get_objects_for_html())
        return main_content, sidebar_content, opts

    def _get_objects_for_html(self, list_to_append=None, obj=None, exclude_model_names=None):
        list_to_append = super()._get_objects_for_html(list_to_append, obj, exclude_model_names)
        if obj is None:
            for axis in self.chartaxis_set.all():
                list_to_append = super()._get_objects_for_html(list_to_append, axis, ['chart'])

        return list_to_append


class ChartAxis(models.Model):
    label = models.CharField(max_length=400, default='', blank=True)
    position_choices = (
        (0, 'left'),
        (1, 'right'),
        )
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    min = models.FloatField(blank=True, null=True)
    max = models.FloatField(blank=True, null=True)
    show_bars = models.BooleanField(default=False, help_text="Show bars")
    show_plot_points = models.BooleanField(default=False, help_text="Show the plots points")
    show_plot_lines_choices = (
        (0, 'No'),
        (1, 'Yes'),
        (2, 'Yes as steps'),)
    show_plot_lines = models.PositiveSmallIntegerField(default=2, help_text="Show the plot lines",
                                                       choices=show_plot_lines_choices)
    stack = models.BooleanField(default=False, help_text="Stack all variables of this axis")
    fill = models.BooleanField(default=False, help_text="Fill all variables of this axis")
    variables = models.ManyToManyField(Variable)
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Y Axis'
        verbose_name_plural = 'Y Axis'


class Pie(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    radius = models.PositiveSmallIntegerField(default=100, validators=[MaxValueValidator(100), MinValueValidator(1)])
    innerRadius = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100), MinValueValidator(0)])
    variables = models.ManyToManyField(Variable, blank=True)
    variable_properties = models.ManyToManyField(VariableProperty, blank=True)

    def __str__(self):
        return text_type(str(self.id) + ': ' + self.title)

    def visible(self):
        return True

    def variables_list(self, exclude_list=[]):
        return [item.pk for item in self.variables.exclude(pk__in=exclude_list)]

    def gen_html(self, **kwargs):
        """
        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs['widget_pk'] if 'widget_pk' in kwargs else 0
        widget_extra_css_class = kwargs["widget_extra_css_class"] if "widget_extra_css_class" in kwargs else ""
        main_template = get_template('pie.html')
        sidebar_template = get_template('chart_legend.html')
        main_content = main_template.render(dict(pie=self, widget_pk=widget_pk, widget_extra_css_class=widget_extra_css_class,))
        sidebar_content = sidebar_template.render(dict(chart=self, pie=1, widget_pk=widget_pk, widget_extra_css_class=widget_extra_css_class,))
        opts = dict()
        opts['flot'] = True
        opts['topbar'] = True
        return main_content, sidebar_content, opts


class Form(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    button = models.CharField(max_length=50, default='Ok')
    control_items = models.ManyToManyField(ControlItem, related_name='control_items_form',
                                           limit_choices_to={'type': '0'}, blank=True)
    hidden_control_items_to_true = models.ManyToManyField(ControlItem, related_name='hidden_control_items_form',
                                                          limit_choices_to={'type': '0'}, blank=True)

    def __str__(self):
        return text_type(str(self.id) + ': ' + self.title)

    def visible(self):
        return True

    def web_id(self):
        return "form-" + self.id.__str__()

    def control_items_list(self):
        return [item.pk for item in self.control_items]

    def hidden_control_items_to_true_list(self):
        return [item.pk for item in self.hidden_control_items_to_true]


class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    link_title = models.SlugField(max_length=80, default='')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.link_title.replace(' ', '_')


class ControlPanel(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    items = models.ManyToManyField(ControlItem, blank=True)
    forms = models.ManyToManyField(Form, blank=True)

    def __str__(self):
        return str(self.id) + ': ' + self.title

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs['widget_pk'] if 'widget_pk' in kwargs else 0
        widget_extra_css_class = kwargs["widget_extra_css_class"] if "widget_extra_css_class" in kwargs else ""
        visible_element_list = kwargs['visible_control_element_list'] if 'visible_control_element_list' in kwargs else []
        visible_form_list = kwargs['visible_form_list'] if 'visible_form_list' in kwargs else []
        main_template = get_template('control_panel.html')
        main_content = main_template.render(dict(control_panel=self,
                                                 visible_control_element_list=visible_element_list,
                                                 visible_form_list=visible_form_list,
                                                 uuid=uuid4().hex, widget_pk=widget_pk,
                                                 widget_extra_css_class=widget_extra_css_class,))
        sidebar_content = None
        opts = dict()
        opts['flot'] = False
        for item in self.items.all():
            if item.display_value_options is not None and item.display_value_options.type == 3:
                opts['flot'] = True
        for form in self.forms.all():
            for item in form.control_items.all():
                if item.display_value_options is not None and item.display_value_options.type == 3:
                    opts['flot'] = True
        opts["object_config_list"] = set()
        opts["object_config_list"].update(self._get_objects_for_html())
        opts["custom_fields_list"] = {'variable': [{'name': 'refresh-requested-timestamp', 'value': ""},
                                                   {'name': 'value-timestamp', 'value': ''}, ],
                                      'variableproperty': [{'name': 'refresh-requested-timestamp', 'value': ""},
                                                           {'name': 'value-timestamp', 'value': ''}, ],
                                      }
        return main_content, sidebar_content, opts


class CustomHTMLPanel(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    html = models.TextField()
    variables = models.ManyToManyField(Variable, blank=True)
    variable_properties = models.ManyToManyField(VariableProperty, blank=True)

    def __str__(self):
        return str(self.id) + ': ' + self.title

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        widget_pk = kwargs['widget_pk'] if 'widget_pk' in kwargs else 0
        widget_extra_css_class = kwargs["widget_extra_css_class"] if "widget_extra_css_class" in kwargs else ""
        main_template = get_template('custom_html_panel.html')
        main_content = main_template.render(dict(custom_html_panel=self, widget_pk=widget_pk, widget_extra_css_class=widget_extra_css_class,))
        sidebar_content = None
        opts = dict()
        opts["object_config_list"] = set()
        opts["object_config_list"].update(self._get_objects_for_html())
        return main_content, sidebar_content, opts


class ProcessFlowDiagramItem(models.Model):
    id = models.AutoField(primary_key=True)
    control_item = models.ForeignKey(ControlItem, default=None, blank=True, null=True, on_delete=models.CASCADE)
    top = models.PositiveIntegerField(blank=True, default=0)
    left = models.PositiveIntegerField(blank=True, default=0)
    font_size = models.PositiveSmallIntegerField(default=14)
    width = models.PositiveIntegerField(blank=True, default=0)
    height = models.PositiveIntegerField(blank=True, default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        if self.control_item.label != '':
            return str(self.id) + ": " + self.control_item.label
        else:
            return str(self.id) + ": " + self.control_item.name


class ProcessFlowDiagram(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    background_image = models.ImageField(upload_to="img/", height_field='url_height', width_field='url_width',
                                         verbose_name="background image", blank=True)
    type_choices = ((0, 'HTML'), (1, 'SVG'),)
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices,
                                            help_text='HTML is not responsive and can display control element<br>'
                                                      'SVG is responsive and cannot display control element')
    process_flow_diagram_items = models.ManyToManyField(ProcessFlowDiagramItem, blank=True)
    url_height = models.PositiveIntegerField(editable=False, default="100", null=True)
    url_width = models.PositiveIntegerField(editable=False, default="100", null=True)

    def __str__(self):
        if self.title:
            return str(self.id) + ": " + self.title
        else:
            return str(self.id) + ": " + self.background_image.name

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        main_template = get_template('process_flow_diagram.html')
        try:
            widget_pk = kwargs['widget_pk'] if 'widget_pk' in kwargs else 0
            widget_extra_css_class = kwargs["widget_extra_css_class"] if "widget_extra_css_class" in kwargs else ""
            main_content = main_template.render(dict(process_flow_diagram=self,
                                                     height_width_ratio=100 *
                                                     float(self.url_height) / float(self.url_width),
                                                     uuid=uuid4().hex, widget_pk=widget_pk,
                                                     widget_extra_css_class=widget_extra_css_class,))
        except ValueError:
            logger.info("ProcessFlowDiagram (%s) has no background image defined" % self)
            main_content = None
        sidebar_content = None
        opts = dict()
        opts["object_config_list"] = set()
        opts["object_config_list"].update(self._get_objects_for_html())

        return main_content, sidebar_content, opts


class SlidingPanelMenu(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    position_choices = ((0, 'Control Menu'), (1, 'left'), (2, 'right'))
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    control_panel = models.ForeignKey(ControlPanel, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title


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
                return '', '', ''
        except:
            logger.error(f'{content_model} unhandled exception', exc_info=True)
            # todo del self
            return '', '', ''

    def _import_content_model(self):
        content_class_str = self.content_model
        class_name = content_class_str.split('.')[-1]
        class_path = content_class_str.replace('.' + class_name, '')
        try:
            mod = __import__(class_path, fromlist=[class_name.__str__()])
            content_class = getattr(mod, class_name.__str__())
            if isinstance(content_class, models.base.ModelBase):
                return content_class.objects.get(pk=self.content_pk)
        except ModuleNotFoundError:
            logger.info(f"{class_name} of {class_path} not found. A module is not installed ?")
        except:
            logger.error(f'{class_path} unhandled exception', exc_info=True)
        return None

    def __str__(self):
        return '%s [%d] %s' % (self.content_model.split('.')[-1], self.content_pk, self.content_str)  # todo add more infos


class CssClass(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    css_class = models.CharField(max_length=250, default='')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Css Classes'


class Widget(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    page = models.ForeignKey(Page, null=True, default=None, blank=True, on_delete=models.SET_NULL)
    row_choices = (
        (0, "1. row"), (1, "2. row"), (2, "3. row"), (3, "4. row"), (4, "5. row"), (5, "6. row"), (6, "7. row"),
        (7, "8. row"), (8, "9. row"), (9, "10. row"), (10, "11. row"), (11, "12. row"),)
    row = models.PositiveSmallIntegerField(default=0, choices=row_choices)
    col_choices = ((0, "1. col"), (1, "2. col"), (2, "3. col"), (3, "4. col"))
    col = models.PositiveSmallIntegerField(default=0, choices=col_choices)
    size_choices = ((4, 'page width'), (3, '3/4 page width'), (2, '1/2 page width'), (1, '1/4 page width'))
    size = models.PositiveSmallIntegerField(default=4, choices=size_choices)
    visible = models.BooleanField(default=True)
    content = models.ForeignKey(WidgetContent, null=True, default=None, on_delete=models.SET_NULL)
    extra_css_class = models.ForeignKey(CssClass, null=True, default=None, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['row', 'col']

    def __str__(self):
        if self.title is not None and self.page:
            return str(self.id) + ': ' + self.page.title + ', ' + self.title
        else:
            return str(self.id) + ': ' + 'None, None'

    def css_class(self):
        widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-12"
        if self.size == 3:
            widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-9"
        elif self.size == 2:
            widget_size = "col-xs-12 col-sm-12 col-md-6 col-lg-6"
        elif self.size == 1:
            widget_size = "col-xs-12 col-sm-6 col-md-6 col-lg-3"
        return 'widget_row_' + str(self.row) + ' widget_col_' + str(self.col) + ' ' + widget_size


class View(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    description = models.TextField(default='', verbose_name="Description", null=True)
    link_title = models.SlugField(max_length=80, default='')
    pages = models.ManyToManyField(Page)
    sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu, blank=True)
    logo = models.ImageField(upload_to="img/", verbose_name="Overview Picture", blank=True)
    visible = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)
    show_timeline = models.BooleanField(default=True)
    theme = models.ForeignKey(Theme, blank=True, null=True, default=None, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']


class GroupDisplayPermission(models.Model):
    hmi_group = models.OneToOneField(Group, blank=True, null=True, on_delete=models.CASCADE)
    type_choices = ((0, 'allow'), (1, 'exclude'),)

    def __str__(self):
        if self.hmi_group is not None:
            return self.hmi_group.name
        else:
            return "Users without any group"


class PieGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    pies = models.ManyToManyField(Pie, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class PageGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    pages = models.ManyToManyField(Page, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class SlidingPanelMenuGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class ChartGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    charts = models.ManyToManyField(Chart, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class ControlItemGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    control_items = models.ManyToManyField(ControlItem, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class FormGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    forms = models.ManyToManyField(Form, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class WidgetGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    widgets = models.ManyToManyField(Widget, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class CustomHTMLPanelGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    custom_html_panels = models.ManyToManyField(CustomHTMLPanel, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class ViewGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    views = models.ManyToManyField(View, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)


class ProcessFlowDiagramGroupDisplayPermission(models.Model):
    group_display_permission = models.OneToOneField(GroupDisplayPermission, null=True, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(default=0, choices=GroupDisplayPermission.type_choices,
                                            help_text='If allow: only selected items can be seen by the group.'
                                                      '<br>If exclude: allows all items except the selected ones.')
    process_flow_diagram = models.ManyToManyField(ProcessFlowDiagram, blank=True, related_name='groupdisplaypermission')

    def __str__(self):
        return str(self.group_display_permission)
