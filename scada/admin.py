# -*- coding: utf-8 -*-
from django.contrib import admin
from scada.models import InputConfig
from scada.models import ControllerConfig
from scada.models import ScalingConfig
from scada.models import UnitConfig
from scada.models import RecordedData
from scada.models import RecordedTime



class InputConfigAdmin(admin.ModelAdmin):
   # list_display = ('VariableName', 'Description', 'Address', 'Controller_id', 'active','Unit','Scaling_id')
    list_display = ('variable_name', 'description', 'address','active','unit')
   # list_filter = ['Controller_id']
    list_filter = ['variable_name']
    search_fields = ['description']
admin.site.register(InputConfig,InputConfigAdmin)

class ControllerConfigAdmin(admin.ModelAdmin):
    # ...
    list_display = ('ip_address', 'port','description')
    list_filter = ['ip_address']
    search_fields = ['description']
admin.site.register(ControllerConfig,ControllerConfigAdmin)

class ScalingConfigAdmin(admin.ModelAdmin):
    list_display = ('description', 'min_value', 'max_value','bit')
    list_filter = ['bit']
    search_fields = ['description']
admin.site.register(ScalingConfig,ScalingConfigAdmin)    

class UnitConfigAdmin(admin.ModelAdmin):
    list_display = ('unit', 'description')
    list_filter = ['unit']
    search_fields = ['description']
admin.site.register(UnitConfig,UnitConfigAdmin)

class RecordedTimeAdmin(admin.ModelAdmin):
	list_display = ('id','timestamp')
admin.site.register(RecordedTime,RecordedTimeAdmin)

class RecordedDataAdmin(admin.ModelAdmin):
    list_display = ('time','value')
    list_filter = ['time']
admin.site.register(RecordedData,RecordedDataAdmin)
