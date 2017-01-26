# -*- coding: utf-8 -*-
from pyscada.models import Device
from pyscada.models import Variable
from pyscada.models import Scaling, Color
from pyscada.models import Unit
from pyscada.models import DeviceWriteTask
from pyscada.models import Log
from pyscada.models import BackgroundTask
from pyscada.models import Event
from pyscada.models import RecordedEvent, RecordedData
from pyscada.models import Mail
from pyscada.utils import update_variable_set

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
from django.conf import settings
from django.contrib.admin import AdminSite

import datetime


## Custom AdminSite

class PyScadaAdminSite(AdminSite):
    site_header = 'PyScada administration'

## rest


# class VariableImportAdminForm(forms.ModelForm):
#     json_configuration = forms.CharField(widget=forms.Textarea)
# 
#     class Meta:
#         fields = []
#         model = Variable
# 
# class VariableImportAdmin(admin.ModelAdmin):
#     actions = None
#     form = VariableImportAdminForm
#     fields = ('json_configuration',)
#     list_display = ('name','active')
# 
#     def save_model(self, request, obj, form, change):
#         update_variable_set(form.cleaned_data['json_configuration'])
# 
#     def __init__(self, *args, **kwargs):
#         super(VariableImportAdmin, self).__init__(*args, **kwargs)
#         self.list_display_links = (None, )
# 
# 
# class VariableConfigFileImport(Variable):
#     class Meta:
#         proxy = True
        
class VariableState(Variable):
    class Meta:
        proxy = True
        
class VariableStateAdmin(admin.ModelAdmin):
    list_display = ('name','last_value')
    list_filter = ('device__short_name', 'active','unit__unit','value_class')
    list_display_links = ()
    list_per_page = 10
    actions = None
    search_fields = ('name',)
    def last_value(self, instance):
        element = RecordedData.objects.last_element(variable_id=instance.pk)
        if element:
            return  datetime.datetime.fromtimestamp(\
                element.time_value()).strftime('%Y-%m-%d %H:%M:%S')\
                 + ' : ' + element.value().__str__() + ' ' + instance.unit.unit
        else:
            return ' - : NaN ' + instance.unit.unit

class DeviceAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DeviceAdminFrom, self).__init__(*args, **kwargs)
        w = self.fields['device_type'].widget
        # return a list of installed drivers for device classes
        device_type_choices = (('generic','no Device'),)
        # Check if psutil is installed for the system statistics device module
        try:
            import psutil
            device_type_choices += (('systemstat','Local System Monitoring',),)
        except ImportError:
            pass
        # Check if pymodbus is installed for the modbus device module
        try:
            import pymodbus
            device_type_choices += (('modbus','Modbus Device',),)
        except ImportError:
            pass
        # Check if pymodbus is installed for the modbus device module
        try:
            import smbus
            device_type_choices += (('smbus','SMBus/I2C Device',),)
        except ImportError:
            pass
        try:
            import visa
            device_type_choices += (('visa','VISA Device',),)
        except ImportError:
            pass
        
        if 'pyscada.phant' in settings.INSTALLED_APPS:
            device_type_choices += (('phant','Phant Device',),)
        
        w.choices = device_type_choices

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id','short_name','description','active',)
    list_display_links = ('short_name', 'description')
    form = DeviceAdminFrom

class VarieblesAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VarieblesAdminFrom, self).__init__(*args, **kwargs)
        wtf = Color.objects.all();
        w = self.fields['chart_line_color'].widget
        color_choices = []
        for choice in wtf:
            color_choices.append((choice.id,choice.color_code()))
        w.choices = color_choices
        # override w.render_option method
        def render_option_color(self,selected_choices, option_value, option_label):
            html = self._render_option(selected_choices, option_value, option_label.upper())
            font_color = hex(int('ffffff',16)-int(option_label[1::],16))[2::]
            return html.replace('<option','<option style="background: %s; color: #%s"'%(option_label,font_color))
        import types
        from django.forms.widgets import Select
        w.widget._render_option = w.widget.render_option # copy old method 
        f = types.MethodType(render_option_color, w.widget,Select)
        w.widget.render_option = f # add new method
        
class VarieblesAdmin(admin.ModelAdmin):
    list_display = ('id','name','description','unit','device_name','value_class','active','writeable',)
    list_editable = ('active','writeable',)
    list_display_links = ('name',)
    list_filter = ('device__short_name', 'active','writeable','unit__unit','value_class')
    search_fields = ['name',]
    form = VarieblesAdminFrom
    def device_name(self, instance):
        return instance.device.short_name
    def unit(self, instance):
        return instance.unit.unit
    

class DeviceWriteTaskAdmin(admin.ModelAdmin):
    list_display = ('id','name','value','user_name','start_time','done','failed',)
    #list_editable = ('active','writeable',)
    list_display_links = ('name',)
    list_filter = ('done', 'failed',)
    raw_id_fields = ('variable',)
    def name(self, instance):
        return instance.variable.name
    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'
    def start_time(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime('%Y-%m-%d %H:%M:%S')
    def has_delete_permission(self, request, obj=None):
        return False

class LogAdmin(admin.ModelAdmin):
    list_display = ('id','time','level','message_short','user_name',)
    list_display_links = ('message_short',)
    list_filter = ('level', 'user')
    search_fields = ['message',]
    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'
    def time(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False



class BackgroundTaskAdmin(admin.ModelAdmin):
    list_display = ('id','label','message','load','last_update','running_since','done','failed')
    list_display_links = ('label',)
    list_filter = ('done','failed')
    search_fields = ['variable',]
    def last_update(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    def running_since(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime('%Y-%m-%d %H:%M:%S')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class RecordedEventAdmin(admin.ModelAdmin):
    list_display = ('id','event','time_begin','time_end','active',)
    list_display_links = ('event',)
    list_filter = ('event','active')
    readonly_fields = ('time_begin','time_end',)

class MailAdmin(admin.ModelAdmin):
    list_display = ('id','subject','message','last_update','done','send_fail_count',)
    list_display_links = ('subject',)
    list_filter = ('done',)
    def last_update(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')

class EventAdmin(admin.ModelAdmin):
    list_display = ('id','label','variable','limit_type','level','action',)
    list_display_links = ('id','label',)
    list_filter = ('level','limit_type','action',)
    filter_horizontal = ('mail_recipients',)

    raw_id_fields = ('variable',)

admin_site = PyScadaAdminSite(name='pyscada_admin')
admin_site.register(Device,DeviceAdmin)
admin_site.register(Variable,VarieblesAdmin)
admin_site.register(Scaling)
# admin.site.register(VariableConfigFileImport,VariableImportAdmin)
admin_site.register(Unit)
admin_site.register(Event,EventAdmin)
admin_site.register(RecordedEvent,RecordedEventAdmin)
admin_site.register(Mail,MailAdmin)
admin_site.register(DeviceWriteTask,DeviceWriteTaskAdmin)
admin_site.register(Log,LogAdmin)
admin_site.register(BackgroundTask,BackgroundTaskAdmin)
admin_site.register(VariableState,VariableStateAdmin)
