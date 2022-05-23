# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site

from pyscada.models import Variable
from pyscada.models import Color
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Chart, ChartAxis
from pyscada.hmi.models import Form
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import Page
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import DisplayValueOption, ControlElementOption
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.hmi.models import ProcessFlowDiagramItem
from pyscada.hmi.models import Pie

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
import logging

logger = logging.getLogger(__name__)


class FormListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('form filter')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'form'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        result = list()
        for form in Form.objects.all():
            result.append((form.pk, form.title),)
        return result

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() is not None:
            return queryset.filter(control_items_form__in=self.value())


class ChartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all()
        w = self.fields['variables'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.name + '( ' + choice.unit.description + ' )'))
        w.choices = choices


class ChartAxisInline(admin.TabularInline):
    model = ChartAxis
    filter_vertical = ['variables']

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1


class ChartAdmin(admin.ModelAdmin):
    list_per_page = 100
    # ordering = ['position',]
    search_fields = ['title', ]
    List_display_link = ('title',)
    list_display = ('id', 'title', 'x_axis_label', 'x_axis_linlog',)
    #list_filter = ('widget__page__title', 'widget__title',)
    #form = ChartForm
    save_as = True
    save_as_continue = True
    inlines = [ChartAxisInline]

    def name(self, instance):
        return instance.variables.name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'x_axis_var':
            kwargs['empty_label'] = "Time series"
        return super(ChartAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PieForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all()
        w = self.fields['variables'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.name + '( ' + choice.unit.description + ' )'))
        w.choices = choices


class PieAdmin(admin.ModelAdmin):
    list_per_page = 100
    # ordering = ['position',]
    search_fields = ['name', ]
    filter_horizontal = ('variables', 'variable_properties')
    List_display_link = ('title',)
    list_display = ('id', 'title')
    form = PieForm
    save_as = True
    save_as_continue = True

    def name(self, instance):
        return instance.variables.name


class FormAdmin(admin.ModelAdmin):
    filter_horizontal = ('control_items', 'hidden_control_items_to_true',)
    list_filter = ('controlpanel',)
    save_as = True
    save_as_continue = True


class DisplayValueOptionAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisplayValueOptionAdminFrom, self).__init__(*args, **kwargs)
        wtf = Color.objects.all()
        w1 = self.fields['color_1'].widget
        w2 = self.fields['color_2'].widget
        w3 = self.fields['color_3'].widget
        color_choices = []
        for choice in wtf:
            color_choices.append((choice.id, choice.color_code()))
        w1.choices = color_choices
        w2.choices = color_choices
        w3.choices = color_choices

        def create_option_color(self, name, value, label, selected, index, subindex=None, attrs=None):
            font_color = hex(int('ffffff', 16) - int(label[1::], 16))[2::]
            # attrs = self.build_attrs(attrs,{'style':'background: %s; color: #%s'%(label,font_color)})
            self.option_inherits_attrs = True
            return self._create_option(name, value, label, selected, index, subindex,
                                       attrs={'style': 'background: %s; color: #%s' % (label, font_color)})

        import types
        # from django.forms.widgets import Select
        w1.widget._create_option = w1.widget.create_option  # copy old method
        w1.widget.create_option = types.MethodType(create_option_color, w1.widget)  # replace old with new
        w2.widget._create_option = w2.widget.create_option  # copy old method
        w2.widget.create_option = types.MethodType(create_option_color, w2.widget)  # replace old with new
        w3.widget._create_option = w3.widget.create_option  # copy old method
        w3.widget.create_option = types.MethodType(create_option_color, w3.widget)  # replace old with new
        w1.widget.attrs = {'onchange': 'this.style.backgroundColor=this.options[this.selectedIndex].style.'
                                       'backgroundColor;this.style.color=this.options[this.selectedIndex].style.color'}
        w2.widget.attrs = {'onchange': 'this.style.backgroundColor=this.options[this.selectedIndex].style.'
                                       'backgroundColor;this.style.color=this.options[this.selectedIndex].style.color'}
        w3.widget.attrs = {'onchange': 'this.style.backgroundColor=this.options[this.selectedIndex].style.'
                                       'backgroundColor;this.style.color=this.options[this.selectedIndex].style.color'}


class DisplayValueOptionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'color_type', 'mode', 'timestamp_conversion',),
        }),
        ('Color 1', {
            'fields': ('color_level_1_type', 'color_level_1', 'color_1',),
        }),
        ('Color 2', {
            'fields': ('color_level_2_type', 'color_level_2', 'color_2',),
        }),
        ('Color 3', {
            'fields': ('color_3',),
        }),
    )
    form = DisplayValueOptionAdminFrom
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


class ControlElementOptionAdmin(admin.ModelAdmin):
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


class ControlItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'label', 'type', 'variable', 'variable_property', 'display_value_options',
                    'control_element_options')
    list_filter = ('controlpanel', FormListFilter, 'type',)
    list_editable = ('position', 'label', 'type', 'variable', 'variable_property', 'display_value_options',
                     'control_element_options')
    raw_id_fields = ('variable',)
    save_as = True
    save_as_continue = True


class SlidingPanelMenuForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SlidingPanelMenuForm, self).__init__(*args, **kwargs)
        wtf = ControlItem.objects.all()
        w = self.fields['items'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id,
                            choice.label + " (" + choice.variable.name + ', ' + choice.get_type_display() + ")"))
        w.choices = choices


class SlidingPanelMenuAdmin(admin.ModelAdmin):
    # search_fields = ['name',]
    # filter_horizontal = ('items',)
    # form = SlidingPanelMenuForm
    list_display = ('id', 'title', 'position', 'visible')
    save_as = True
    save_as_continue = True


class WidgetAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id', 'title', 'page', 'row', 'col', 'size', 'content', 'visible', )
    list_editable = ('title', 'page', 'row', 'col', 'size', 'content', 'visible', )
    list_filter = ('page',)
    save_as = True
    save_as_continue = True


class GroupDisplayPermissionAdmin(admin.ModelAdmin):
    filter_horizontal = (
        'pages', 'sliding_panel_menus', 'charts', 'control_items', 'widgets', 'views',
        'custom_html_panels', 'process_flow_diagram', 'forms',)
    save_as = True
    save_as_continue = True


class ControlPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('items', 'forms',)
    save_as = True
    save_as_continue = True


class ViewAdmin(admin.ModelAdmin):
    filter_horizontal = ('pages', 'sliding_panel_menus')
    save_as = True
    save_as_continue = True


class CustomHTMLPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables', 'variable_properties')
    save_as = True
    save_as_continue = True


class PageAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id', 'title', 'link_title', 'position',)
    list_editable = ('title', 'link_title', 'position',)
    list_filter = ('view__title',)
    save_as = True
    save_as_continue = True


class ProcessFlowDiagramItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'control_item', 'top', 'left', 'width', 'height', 'visible', 'font_size',)
    list_editable = ('control_item', 'top', 'left', 'width', 'height', 'visible', 'font_size',)
    # raw_id_fields = ('variable',)
    save_as = True
    save_as_continue = True


class ProcessFlowDiagramAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'background_image',)
    list_editable = ('title', 'type', 'background_image',)
    filter_horizontal = ('process_flow_diagram_items',)
    save_as = True
    save_as_continue = True


admin_site.register(ControlItem, ControlItemAdmin)
admin_site.register(Chart, ChartAdmin)
admin_site.register(Pie, PieAdmin)
admin_site.register(Form, FormAdmin)
admin_site.register(SlidingPanelMenu, SlidingPanelMenuAdmin)
admin_site.register(Page, PageAdmin)
admin_site.register(GroupDisplayPermission, GroupDisplayPermissionAdmin)
admin_site.register(DisplayValueOption, DisplayValueOptionAdmin)
admin_site.register(ControlElementOption, ControlElementOptionAdmin)
admin_site.register(ControlPanel, ControlPanelAdmin)
admin_site.register(CustomHTMLPanel, CustomHTMLPanelAdmin)
admin_site.register(Widget, WidgetAdmin)
admin_site.register(View, ViewAdmin)
admin_site.register(ProcessFlowDiagram, ProcessFlowDiagramAdmin)
admin_site.register(ProcessFlowDiagramItem, ProcessFlowDiagramItemAdmin)
