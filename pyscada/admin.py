# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.models import UnitConfig
from pyscada.models import ClientWriteTask
from pyscada import log
from pyscada.utils import update_variable_set
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms


class VariableAdminForm(forms.ModelForm):
    json_configuration = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Variable

class VariableImportAdmin(admin.ModelAdmin):
    actions = None
    form = VariableAdminForm
    fields = ('json_configuration',)
    list_display = ('variable_name','active')
    
    def save_model(self, request, obj, form, change):
        update_variable_set(form.cleaned_data['json_configuration'])
        #log.debug(form.cleaned_data['json_configuration'])

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
    list_display = ('id','variable_name','description','client_name','value_class','active','writeable',)
    list_editable = ('active','writeable',)
    list_display_links = ('variable_name',)
    list_filter = ('client__short_name', 'active','writeable')
    search_fields = ['variable_name',]
    def client_name(self, instance):
        return instance.client.short_name


class ClientWriteTaskAdmin(admin.ModelAdmin):
    list_display = ('id','variable_name','value','user_name','done','failed',)
    #list_editable = ('active','writeable',)
    list_display_links = ('variable_name',)
    list_filter = ('done', 'failed',)
    def variable_name(self, instance):
        return instance.variable.variable_name
    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'


admin.site.register(Client,ClientAdmin)
admin.site.register(Variable,VarieblesAdmin)
admin.site.register(VariableConfigFileImport,VariableImportAdmin)
admin.site.register(UnitConfig)
admin.site.register(ClientWriteTask,ClientWriteTaskAdmin)