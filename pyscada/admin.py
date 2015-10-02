# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.models import Unit
from pyscada.models import ClientWriteTask
from pyscada.models import Log
from pyscada.models import BackgroundTask
from pyscada.models import RecordedDataCache
from pyscada.models import Event
from pyscada.models import RecordedEvent
from pyscada.models import MailRecipient
from pyscada.models import MailQueue
from pyscada.utils import update_variable_set
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms
import datetime

class VariableAdminForm(forms.ModelForm):
    json_configuration = forms.CharField(widget=forms.Textarea)

    class Meta:
        fields = []
        model = Variable

class VariableImportAdmin(admin.ModelAdmin):
    actions = None
    form = VariableAdminForm
    fields = ('json_configuration',)
    list_display = ('name','active')

    def save_model(self, request, obj, form, change):
        update_variable_set(form.cleaned_data['json_configuration'])

    def __init__(self, *args, **kwargs):
        super(VariableImportAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class VariableConfigFileImport(Variable):
    class Meta:
        proxy = True


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
    list_display = ('id','name','value','user_name','start_time','done','failed',)
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

class RecordedDataCacheAdmin(admin.ModelAdmin):
    list_display = ('id','last_change','name','value','unit','last_update',)
    list_display_links = ('name',)
    list_filter = ('variable__client','variable__unit')
    search_fields = ['variable__name',]
    readonly_fields = ('last_change','last_update','time',)
    def name(self,instance):
        return instance.variable.name
    def  unit(self,instance):
        return instance.variable.unit.unit
    def last_change(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.last_change.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    def last_update(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.time.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
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

class MailQueueAdmin(admin.ModelAdmin):
    list_display = ('id','subject','message','last_update','done','send_fail_count',)
    list_display_links = ('subject',)
    list_filter = ('done',)
    filter_horizontal = ('mail_recipients',)
    def last_update(self,instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    
admin.site.register(Client,ClientAdmin)
admin.site.register(Variable,VarieblesAdmin)
admin.site.register(VariableConfigFileImport,VariableImportAdmin)
admin.site.register(Unit)
admin.site.register(Event)
admin.site.register(RecordedEvent,RecordedEventAdmin)
admin.site.register(MailRecipient)
admin.site.register(MailQueue,MailQueueAdmin)
admin.site.register(ClientWriteTask,ClientWriteTaskAdmin)
admin.site.register(Log,LogAdmin)
admin.site.register(BackgroundTask,BackgroundTaskAdmin)
admin.site.register(RecordedDataCache,RecordedDataCacheAdmin)
