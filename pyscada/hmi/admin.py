# -*- coding: utf-8 -*-
from pyscada.hmi.models import VariableDisplayPropery
from pyscada.models import Variable
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Chart
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import Page
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import ChartSet
from pyscada.hmi.models import Widget


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
            choices.append((choice.id, choice.variable_name+'( '+ choice.unit.description +' )'))
        w.choices = choices

class ChartAdmin(admin.ModelAdmin):
    list_per_page = 100
    #ordering = ['position',]
    search_fields = ['variable_name',]
    filter_horizontal = ('variables',)
    list_display = ('title',)
    form = ChartForm
    def variable_name(self, instance):
        return instance.variables.variable_name


class ControlItemAdmin(admin.ModelAdmin):
    list_display = ('id','position','label','type','variable',)

class SlidingPanelMenuForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(SlidingPanelMenuForm, self).__init__(*args, **kwargs)
        wtf = ControlItem.objects.all();
        w = self.fields['items'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.label+" ("+ choice.variable.variable_name + ', ' + choice.get_type_display() + ")"))
        w.choices = choices

class SlidingPanelMenuAdmin(admin.ModelAdmin):
        #search_fields = ['variable_name',]
        #filter_horizontal = ('items',)
        #form = SlidingPanelMenuForm
        list_display = ('id',)
        
        
class VariableDisplayProperyAdmin(admin.ModelAdmin):
    search_fields = ['hmi_variable__variable_name',]
    list_display = ('variable_name','short_name','chart_line_color','chart_line_thickness',)
    def variable_name(self, instance):
        return instance.hmi_variable.variable_name
 
class WidgetAdmin(admin.ModelAdmin):
    list_display_links = ('id',)
    list_display = ('id','title','page','row','col','size','chart','chart_set','control_panel','custom_html_panel',)
    list_editable = ('title','page','row','col','size','chart','chart_set','control_panel','custom_html_panel',)
    
        
admin.site.register(ControlItem,ControlItemAdmin)
admin.site.register(Chart,ChartAdmin)
admin.site.register(SlidingPanelMenu,SlidingPanelMenuAdmin)
admin.site.register(Page)
admin.site.register(GroupDisplayPermission)
admin.site.register(VariableDisplayPropery,VariableDisplayProperyAdmin)

admin.site.register(ControlPanel)
admin.site.register(CustomHTMLPanel)
admin.site.register(ChartSet)
admin.site.register(Widget,WidgetAdmin)
