# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.models import Unit
from pyscada.models import ClientWriteTask
from pyscada.models import Log
from pyscada.models import BackgroundTask
from pyscada.models import RecordedDataCache
from pyscada.models import Event
from pyscada.utils import update_variable_set
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
import datetime


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id','short_name','description','active',)
    list_display_links = ('short_name', 'description')


class VarieblesAdmin(admin.ModelAdmin):
    list_display = ('id','name','description','client_name','value_class','active','writeable',)
    list_editable = ('active','writeable',)
    list_display_links = ('name',)
    list_filter = ('client__short_name', 'active','writeable')
    search_fields = ['name',]
    def client_name(self, instance):
        return instance.client.short_name


class ClientWriteTaskAdmin(admin.ModelAdmin):
    list_display = ('id','name','value','user_name','done','failed',)
    #list_editable = ('active','writeable',)
    list_display_links = ('name',)
    list_filter = ('done', 'failed',)
    def name(self, instance):
        return instance.variable.name
    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'
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

class RecordedDataCacheAdmin(admin.ModelAdmin):
    list_display = ('id','name','value','unit','last_update_time','last_change_time',)
    list_display_links = ('name',)
    list_filter = ('variable__client','variable__unit')
    search_fields = ['variable__name',]
    def name(self,instance):
        return instance.variable.name
    def unit(self,instance):
        return instance.variable.unit.unit
    def last_update_time(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.last_update)).strftime('%Y-%m-%d %H:%M:%S')
    def last_change_time(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.last_change)).strftime('%Y-%m-%d %H:%M:%S')
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
        
admin.site.register(Client,ClientAdmin)
admin.site.register(Variable,VarieblesAdmin)
admin.site.register(Unit)
admin.site.register(Event)
admin.site.register(ClientWriteTask,ClientWriteTaskAdmin)
admin.site.register(Log,LogAdmin)
admin.site.register(BackgroundTask,BackgroundTaskAdmin)
admin.site.register(RecordedDataCache,RecordedDataCacheAdmin)