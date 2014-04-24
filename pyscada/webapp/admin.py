# -*- coding: utf-8 -*-
from pyscada.webapp.models import VariableDisplayPropery
from pyscada.models import Variable
from pyscada.webapp.models import ControlItem
from pyscada.webapp.models import Chart
from pyscada.webapp.models import SlidingPanelMenu
from pyscada.webapp.models import Page
from pyscada.webapp.models import GroupDisplayPermisions

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
    ordering = ['position',]
    search_fields = ['variable_name',]
    filter_horizontal = ('variables',)
    list_display = ('label','position','size',)
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
       # search_fields = ['variable_name',]
        filter_horizontal = ('items',)
        form = SlidingPanelMenuForm

class VariableDisplayProperyAdmin(admin.ModelAdmin):
    search_fields = ['webapp_variable__variable_name',]
    list_display = ('variable_name','short_name','chart_line_color','chart_line_thickness',)
    def variable_name(self, instance):
        return instance.webapp_variable.variable_name
        
admin.site.register(ControlItem,ControlItemAdmin)
admin.site.register(Chart,ChartAdmin)
admin.site.register(SlidingPanelMenu,SlidingPanelMenuAdmin)
admin.site.register(Page)
admin.site.register(GroupDisplayPermisions)
admin.site.register(VariableDisplayPropery,VariableDisplayProperyAdmin)