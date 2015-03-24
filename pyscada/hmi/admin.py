# -*- coding: utf-8 -*-
from pyscada.core.models import Variable
from pyscada.hmi.models import HMIVariable
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Chart
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import Page
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.hmi.models import ProcessFlowDiagramItem
#from pyscada.hmi.models import ChartSet
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View

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
    list_display = ('id','title',)
    form = ChartForm
    def name(self, instance):
        return instance.variables.name


class ControlItemAdmin(admin.ModelAdmin):
    list_display = ('id','position','label','type','variable',)

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
        list_display = ('id',)

class PageAdmin(admin.ModelAdmin):
        list_display = ('id','title','link_title','position')
        
class HMIVariableAdmin(admin.ModelAdmin):
    search_fields = ['hmi_variable__name',]
    list_display = ('name','short_name','chart_line_color','chart_line_thickness',)
    def name(self, instance):
        return instance.hmi_variable.name
 
class WidgetAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id','title','page','row','col','size','chart','control_panel','custom_html_panel',)
    list_editable = ('title','page','row','col','size','chart','control_panel','custom_html_panel',)

class GroupDisplayPermissionAdmin(admin.ModelAdmin):
    filter_horizontal = ('pages','sliding_panel_menus','charts','control_items','widgets','views','custom_html_panels','process_flow_diagram')

class ControlPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('items',)
    
class ViewAdmin(admin.ModelAdmin):
    filter_horizontal = ('pages','sliding_panel_menus')

class CustomHTMLPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ('variables',)

admin.site.register(ControlItem,ControlItemAdmin)
admin.site.register(Chart,ChartAdmin)
admin.site.register(SlidingPanelMenu,SlidingPanelMenuAdmin)
admin.site.register(Page,PageAdmin)
admin.site.register(GroupDisplayPermission,GroupDisplayPermissionAdmin)
admin.site.register(HMIVariable,HMIVariableAdmin)

admin.site.register(ControlPanel,ControlPanelAdmin)
admin.site.register(CustomHTMLPanel,CustomHTMLPanelAdmin)
admin.site.register(ProcessFlowDiagram)
admin.site.register(ProcessFlowDiagramItem)
admin.site.register(Widget,WidgetAdmin)
admin.site.register(View,ViewAdmin)
