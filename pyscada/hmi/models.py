# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable, VariableProperty

from django.db import models
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.template.loader import get_template


from six import text_type
import traceback
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class WidgetContentModel(models.Model):

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        return '', ''

    def create_widget_content_entry(self):
        def fullname(o):
            return o.__module__ + "." + o.__class__.__name__
        wc = WidgetContent(content_pk=self.pk,
                           content_model=fullname(self),
                           content_str=self.__str__())
        wc.save()

    class Meta:
        abstract = True


@python_2_unicode_compatible
class ControlItem(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default='')
    position = models.PositiveSmallIntegerField(default=0)
    type_choices = (
        (0, 'label blue'),
        (1, 'label light blue'),
        (2, 'label ok'),
        (3, 'label warning'),
        (4, 'label alarm'),
        (7, 'label alarm inverted'),
        (5, 'Control Element'),
        (6, 'Display Value'),)
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices)
    variable = models.ForeignKey(Variable, null=True, blank=True, on_delete=models.CASCADE)
    variable_property = models.ForeignKey(VariableProperty, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['position']

    def __str__(self):
        if self.variable_property:
            return self.id.__str__() + "-" + self.variable_property.name.replace(' ', '_')
        elif self.variable:
            return self.id.__str__() + "-" + self.variable.name.replace(' ', '_')

    def web_id(self):
        if self.variable_property:
            return "controlitem-" + self.id.__str__() + "-" + self.variable_property.name.replace(' ', '_')
        elif self.variable:
            return "controlitem-" + self.id.__str__() + "-" + self.variable.name.replace(' ', '_')

    def web_class_str(self):
        if self.variable_property:
            return 'prop-%d' % self.variable_property_id
        elif self.variable:
            return 'var-%d' % self.variable_id

    def active(self):
        if self.variable_property:
            return True
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
            return self.variable_property.value
        elif self.variable:
            return self.variable.value

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


@python_2_unicode_compatible
class Chart(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    x_axis_label = models.CharField(max_length=400, default='', blank=True)
    x_axis_ticks = models.PositiveSmallIntegerField(default=6)
    y_axis_label = models.CharField(max_length=400, default='', blank=True)
    y_axis_min = models.FloatField(default=0)
    y_axis_max = models.FloatField(default=100)
    variables = models.ManyToManyField(Variable)

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
        main_template = get_template('chart.html')
        sidebar_template = get_template('chart_legend.html')
        main_content = main_template.render(dict(chart=self, widget_pk=widget_pk))
        sidebar_content = sidebar_template.render(dict(chart=self, widget_pk=widget_pk))
        return main_content, sidebar_content


@python_2_unicode_compatible
class XYChart(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    x_axis_label = models.CharField(max_length=400, default='', blank=True)
    x_axis_var = models.ForeignKey(Variable, default=None, related_name='x_axis_var', null=True,
                                   on_delete=models.SET_NULL)
    x_axis_linlog = models.BooleanField(default=False, help_text="False->Lin / True->Log")
    y_axis_label = models.CharField(max_length=400, default='', blank=True)
    y_axis_plotpoints = models.BooleanField(default=False, help_text="Show the plots points")
    y_axis_uniquescale = models.BooleanField(default=True, help_text="To have a unique scale for all the y axis")
    variables = models.ManyToManyField(Variable, related_name='variables_xy_chart')

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
        main_template = get_template('xy_chart.html')
        sidebar_template = get_template('xy_chart_legend.html')
        main_content = main_template.render(dict(xy_chart=self, widget_pk=widget_pk))
        sidebar_content = sidebar_template.render(dict(xy_chart=self, widget_pk=widget_pk))
        return main_content, sidebar_content


@python_2_unicode_compatible
class Pie(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    radius = models.CharField(max_length=10, default='auto', help_text="auto or between 0 and 1 or value in pixel")
    innerRadius = models.PositiveSmallIntegerField(default=0, help_text="between 0 and 1 or value in pixel")
    variables = models.ManyToManyField(Variable)

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
        main_template = get_template('pie.html')
        sidebar_template = get_template('chart_legend.html')
        main_content = main_template.render(dict(pie=self, widget_pk=widget_pk))
        sidebar_content = sidebar_template.render(dict(chart=self, widget_pk=widget_pk))
        return main_content, sidebar_content


@python_2_unicode_compatible
class DropDownItem(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    value = models.CharField(max_length=400, default='')

    def __str__(self):
        return text_type(str(self.id) + ': ' + self.title)

    def visible(self):
        return True


@python_2_unicode_compatible
class DropDown(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    variable = models.ForeignKey(Variable, null=True, blank=True, on_delete=models.SET_NULL)
    variable_property = models.ForeignKey(VariableProperty, null=True, blank=True, on_delete=models.SET_NULL)
    empty = models.BooleanField(default=False)
    empty_value = models.CharField(max_length=30, default='------')
    items = models.ManyToManyField(DropDownItem)

    def __str__(self):
        return text_type(str(self.id) + ': ' + self.title)

    def visible(self):
        return True

    def dropdown_items_list(self):
        return [item.pk for item in self.items]

    def items_list(self):
        return ",\n".join([i.title for i in self.items.all()])

    def web_id(self):
        if self.variable_property:
            return "dropdown-" + self.id.__str__() + "-" + self.variable_property.name.replace(' ', '_')
        elif self.variable:
            return "dropdown-" + self.id.__str__() + "-" + self.variable.name.replace(' ', '_')

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
            return self.variable_property.value
        elif self.variable:
            return self.variable.value

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


@python_2_unicode_compatible
class Form(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    button = models.CharField(max_length=50, default='Ok')
    control_items = models.ManyToManyField(ControlItem, related_name='control_items_form',
                                           limit_choices_to={'type': '5'}, blank=True)
    dropdowns = models.ManyToManyField(DropDown, related_name='dropdowns_form', blank=True)
    hidden_control_items_to_true = models.ManyToManyField(ControlItem, related_name='hidden_control_items_form',
                                                          limit_choices_to={'type': '5'}, blank=True)

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

    def dropdown_list(self):
        return [item.pk for item in self.dropdowns]


@python_2_unicode_compatible
class Page(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    link_title = models.SlugField(max_length=80, default='')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.link_title.replace(' ', '_')


@python_2_unicode_compatible
class ControlPanel(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    items = models.ManyToManyField(ControlItem, blank=True)
    dropdowns = models.ManyToManyField(DropDown, blank=True)
    forms = models.ManyToManyField(Form, blank=True)

    def __str__(self):
        return str(self.id) + ': ' + self.title

    def gen_html(self, **kwargs):
        """

        :return: main panel html and sidebar html as
        """
        visible_element_list = kwargs['visible_control_element_list'] if 'visible_control_element_list' in kwargs else []
        main_template = get_template('control_panel.html')
        main_content = main_template.render(dict(control_panel=self,
                                                 visible_control_element_list=visible_element_list,
                                                 uuid=uuid4().hex))
        sidebar_content = None
        return main_content, sidebar_content


@python_2_unicode_compatible
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
        main_template = get_template('custom_html_panel.html')
        main_content = main_template.render(dict(custom_html_panel=self))
        sidebar_content = None
        return main_content, sidebar_content


@python_2_unicode_compatible
class ProcessFlowDiagramItem(models.Model):
    id = models.AutoField(primary_key=True)
    label = models.CharField(max_length=400, default='', blank=True)
    type_choices = (
        (0, 'label blue'),
        (1, 'label light blue'),
        (2, 'label ok'),
        (3, 'label warning'),
        (4, 'label alarm'),
        (7, 'label alarm inverted'),
        (5, 'Control Element'),
        (6, 'Display Value'),)
    type = models.PositiveSmallIntegerField(default=0, choices=type_choices)
    variable = models.ForeignKey(Variable, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    top = models.PositiveIntegerField(blank=True, default=0)
    left = models.PositiveIntegerField(blank=True, default=0)
    width = models.PositiveIntegerField(blank=True, default=0)
    height = models.PositiveIntegerField(blank=True, default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        if self.label:
            return str(self.id) + ": " + self.label
        else:
            return str(self.id) + ": " + self.variable.name


@python_2_unicode_compatible
class ProcessFlowDiagram(WidgetContentModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    background_image = models.ImageField(upload_to="img/", verbose_name="background image", blank=True)
    process_flow_diagram_items = models.ManyToManyField(ProcessFlowDiagramItem, blank=True)

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
        main_content = main_template.render(dict(process_flow_diagram=self))
        sidebar_content = None
        return main_content, sidebar_content


@python_2_unicode_compatible
class SlidingPanelMenu(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    position_choices = ((0, 'Control Menu'), (1, 'left'), (2, 'right'))
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    control_panel = models.ForeignKey(ControlPanel, blank=True, null=True, default=None, on_delete=models.SET_NULL)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class WidgetContent(models.Model):
    content_model = models.CharField(max_length=400)
    content_pk = models.PositiveIntegerField()
    content_str = models.CharField(default="", max_length=400)

    def create_panel_html(self, **kwargs):
        content_model = self._import_content_model()
        try:
            if content_model is not None:
                return content_model.gen_html(**kwargs)
            else:
                return '', ''
        except:
            logger.error('%s unhandled exception\n%s' % (content_model, traceback.format_exc()))
            # todo del self
            return '', ''

    def _import_content_model(self):
        content_class_str = self.content_model
        class_name = content_class_str.split('.')[-1]
        class_path = content_class_str.replace('.' + class_name, '')
        try:
            mod = __import__(class_path, fromlist=[class_name.__str__()])
            content_class = getattr(mod, class_name.__str__())
            if isinstance(content_class, models.base.ModelBase):
                return content_class.objects.get(pk=self.content_pk)
            return None
        except:
            logger.error('%s unhandled exception\n%s' % (class_path, traceback.format_exc()))
            return None

    def __str__(self):
        return '%s [%d] %s' % (self.content_model.split('.')[-1], self.content_pk, self.content_str)  # todo add more infos


@python_2_unicode_compatible
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
            widget_size = "col-xs-9 col-sm-9 col-md-9 col-lg-9"
        elif self.size == 2:
            widget_size = "col-xs-6 col-sm-6 col-md-6 col-lg-6"
        elif self.size == 1:
            widget_size = "col-xs-3 col-sm-3 col-md-3 col-lg-3"
        return 'widget_row_' + str(self.row) + ' widget_col_' + str(self.col) + ' ' + widget_size


@python_2_unicode_compatible
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

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']


@python_2_unicode_compatible
class GroupDisplayPermission(models.Model):
    hmi_group = models.OneToOneField(Group, null=True, on_delete=models.SET_NULL)
    pages = models.ManyToManyField(Page, blank=True)
    sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu, blank=True)
    charts = models.ManyToManyField(Chart, blank=True)
    xy_charts = models.ManyToManyField(XYChart, blank=True)
    control_items = models.ManyToManyField(ControlItem, blank=True)
    forms = models.ManyToManyField(Form, blank=True)
    dropdowns = models.ManyToManyField(DropDown, blank=True)
    widgets = models.ManyToManyField(Widget, blank=True)
    custom_html_panels = models.ManyToManyField(CustomHTMLPanel, blank=True)
    views = models.ManyToManyField(View, blank=True)
    process_flow_diagram = models.ManyToManyField(ProcessFlowDiagram, blank=True)

    def __str__(self):
        return self.hmi_group.name
