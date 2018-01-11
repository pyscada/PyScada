# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Variable

from django.db import models
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from six import text_type
import logging

logger = logging.getLogger(__name__)


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
    variable = models.ForeignKey(Variable, null=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return (self.label + " (" + self.variable.name + ")")

    def web_id(self):
        return self.id.__str__() + "-" + self.variable.name.replace(' ', '_')


@python_2_unicode_compatible
class Chart(models.Model):
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

    def visable(self):
        return True

    def variables_list(self, exclude_list=[]):
        return [item.pk for item in self.variables.exclude(pk__in=exclude_list)]


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
class ControlPanel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    items = models.ManyToManyField(ControlItem, blank=True)

    def __str__(self):
        return (str(self.id) + ': ' + self.title)


@python_2_unicode_compatible
class CustomHTMLPanel(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    html = models.TextField()
    variables = models.ManyToManyField(Variable)

    def __str__(self):
        return (str(self.id) + ': ' + self.title)


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
    variable = models.ForeignKey(Variable, default=None, blank=True, null=True)
    top = models.PositiveIntegerField(default=0)
    left = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    visible = models.BooleanField(default=True)

    def __str__(self):
        if self.label:
            return (str(self.id) + ": " + self.label)
        else:
            return (str(self.id) + ": " + self.variable.name)


@python_2_unicode_compatible
class ProcessFlowDiagram(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    background_image = models.ImageField(upload_to="img/", verbose_name="background image", blank=True)
    process_flow_diagram_items = models.ManyToManyField(ProcessFlowDiagramItem, blank=True)

    def __str__(self):
        if self.title:
            return str(self.id) + ": " + self.title
        else:
            return str(self.id) + ": " + self.background_image.name


@python_2_unicode_compatible
class SlidingPanelMenu(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='')
    position_choices = ((0, 'Control Menu'), (1, 'left'), (2, 'right'))
    position = models.PositiveSmallIntegerField(default=0, choices=position_choices)
    control_panel = models.ForeignKey(ControlPanel, blank=True, null=True, default=None)
    visable = models.BooleanField(default=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Widget(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=400, default='', blank=True)
    page = models.ForeignKey(Page, null=True, default=None, blank=True, )
    row_choices = (
        (0, "1. row"), (1, "2. row"), (2, "3. row"), (3, "4. row"), (4, "5. row"), (5, "6. row"), (6, "7. row"),
        (7, "8. row"), (8, "9. row"), (9, "10. row"), (10, "11. row"), (11, "12. row"),)
    row = models.PositiveSmallIntegerField(default=0, choices=row_choices)
    col_choices = ((0, "1. col"), (1, "2. col"), (2, "3. col"), (3, "4. col"))
    col = models.PositiveSmallIntegerField(default=0, choices=col_choices)
    size_choices = ((4, 'page width'), (3, '3/4 page width'), (2, '1/2 page width'), (1, '1/4 page width'))
    size = models.PositiveSmallIntegerField(default=4, choices=size_choices)
    chart = models.ForeignKey(Chart, blank=True, null=True, default=None)
    control_panel = models.ForeignKey(ControlPanel, blank=True, null=True, default=None)
    custom_html_panel = models.ForeignKey(CustomHTMLPanel, blank=True, null=True, default=None)
    process_flow_diagram = models.ForeignKey(ProcessFlowDiagram, blank=True, null=True, default=None)
    visable = models.BooleanField(default=True)

    class Meta:
        ordering = ['row', 'col']

    def __str__(self):
        if self.title is not None and self.page:
            return (str(self.id) + ': ' + self.page.title + ', ' + self.title)
        else:
            return str(self.id) + ': ' + 'None, None'

    def css_class(self):
        widget_size = "col-xs-12 col-sm-12 col-md-12 col-lg-12"
        if self.size == 3:
            widget_size = "col-xs-8 col-sm-8 col-md-8 col-lg-8"
        elif self.size == 2:
            widget_size = "col-xs-6 col-sm-6 col-md-6 col-lg-6"
        elif self.size == 1:
            widget_size = "col-xs-4 col-sm-4 col-md-4 col-lg-4"
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
    visable = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['position']


@python_2_unicode_compatible
class GroupDisplayPermission(models.Model):
    hmi_group = models.OneToOneField(Group)
    pages = models.ManyToManyField(Page, blank=True)
    sliding_panel_menus = models.ManyToManyField(SlidingPanelMenu, blank=True)
    charts = models.ManyToManyField(Chart, blank=True)
    control_items = models.ManyToManyField(ControlItem, blank=True)
    widgets = models.ManyToManyField(Widget, blank=True)
    custom_html_panels = models.ManyToManyField(CustomHTMLPanel, blank=True)
    views = models.ManyToManyField(View, blank=True)
    process_flow_diagram = models.ManyToManyField(ProcessFlowDiagram, blank=True)

    def __str__(self):
        return self.hmi_group.name
