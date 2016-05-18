# -*- coding: utf-8 -*-
from pyscada.models import Variable
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Chart
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import Page
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.hmi.models import ProcessFlowDiagramItem

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms

class ChartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all();
        w = self.fields['variables'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.name+'( '+ choice.unit.description +' )'))
        w.choices = choices

class ChartAdmin(admin.ModelAdmin):
    list_per_page = 100
    #ordering = ['position',]
    search_fields = ['name',]
    filter_horizontal = ('variables',)
    List_display_link = ('title',)
    list_display = ('id','title',)
    list_filter = ('widget__title','widget__page__title')
    form = ChartForm
    def name(self, instance):
        return instance.variables.name


class ControlItemAdmin(admin.ModelAdmin):
    list_display = ('id','position','label','type','variable',)
    list_filter = ('controlpanel',)
    raw_id_fields = ('variable',)

class SlidingPanelMenuForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SlidingPanelMenuForm, self).__init__(*args, **kwargs)
        wtf = ControlItem.objects.all();
        w = self.fields['items'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.label+" ("+ choice.variable.name + ', ' + choice.get_type_display() + ")"))
        w.choices = choices

class SlidingPanelMenuAdmin(admin.ModelAdmin):
        #search_fields = ['name',]
        #filter_horizontal = ('items',)
        #form = SlidingPanelMenuForm
        list_display = ('id',)


class WidgetAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id','title','page','row','col','size','chart','control_panel','custom_html_panel',)
    list_editable = ('title','page','row','col','size','chart','control_panel','custom_html_panel',)
    list_filter = ('page',)

class GroupDisplayPermissionAdmin(admin.ModelAdmin):
    filter_horizontal = ('pages','sliding_panel_menus','charts','control_items','widgets','views','custom_html_panels','process_flow_diagram')

class ControlPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('items',)

class ViewAdmin(admin.ModelAdmin):
    filter_horizontal = ('pages','sliding_panel_menus')

class CustomHTMLPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)

class PageAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id','title','link_title','position',)
    list_editable = ('title','link_title','position',)
    list_filter = ('view__title',)

class ProcessFlowDiagramItemAdmin(admin.ModelAdmin):
    raw_id_fields = ('variable',)

class ProcessFlowDiagramAdmin(admin.ModelAdmin):
    filter_horizontal = ('process_flow_diagram_items',)

admin.site.register(ControlItem,ControlItemAdmin)
admin.site.register(Chart,ChartAdmin)
admin.site.register(SlidingPanelMenu,SlidingPanelMenuAdmin)
admin.site.register(Page,PageAdmin)
admin.site.register(GroupDisplayPermission,GroupDisplayPermissionAdmin)

admin.site.register(ControlPanel,ControlPanelAdmin)
admin.site.register(CustomHTMLPanel,CustomHTMLPanelAdmin)
admin.site.register(Widget,WidgetAdmin)
admin.site.register(View,ViewAdmin)
admin.site.register(ProcessFlowDiagram,ProcessFlowDiagramAdmin)
admin.site.register(ProcessFlowDiagramItem,ProcessFlowDiagramItemAdmin)
