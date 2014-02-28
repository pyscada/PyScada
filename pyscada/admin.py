# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import ClientConfig
from pyscada.models import Variable
from pyscada.models import WebClientChart
from pyscada.models import WebClientPage
from pyscada.models import WebClientSlidingPanelMenu
from pyscada.models import WebClientControlItem
from pyscada.models import UnitConfig
from pyscada.models import ClientWriteTask
from pyscada import log
from pyscada.utils import update_input_config
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django import forms

class ClientConfigFilter(SimpleListFilter):
    title = _('Client')
    if (ClientConfig.objects.count()>0):
        parameter_name = ClientConfig.objects.first().client.description
    else:
        parameter_name = 1
    def lookups(self, request, model_admin):
        choises = list(set(ClientConfig.objects.all().values_list('client__description','client_id')))
        output = []
        for choise in choises:
            output.append((choise[0],_(choise[0]),))
        return tuple(output)
        

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        return queryset.filter(client__description=self.value())    


class ClientConfigAdmin(admin.ModelAdmin):
    list_display = ('key','value','description')
    list_filter = (ClientConfigFilter,)
    def description(self, instance):
        return instance.client.description
    #def id(self, instance):
    #    return instance.client.pk


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
        update_input_config(form.cleaned_data['json_configuration'])
        #log.debug(form.cleaned_data['json_configuration'])

    def __init__(self, *args, **kwargs):
        super(VariableImportAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


class VariableConfigFileImport(Variable):
    class Meta:
        proxy = True


class WebClientChartForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(WebClientChartForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all();
        w = self.fields['variables'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.variable_name))
        w.choices = choices

class WebClientChartAdmin(admin.ModelAdmin):
    list_per_page = 100
    ordering = ['position',]
    search_fields = ['variable_name',]
    filter_horizontal = ('variables',)
    list_display = ('label','page','position','size',)
    form = WebClientChartForm
    def variable_name(self, instance):
        return instance.variables.variable_name


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id','short_name','description','active',)
    list_display_links = ('short_name', 'description')

class WebClientSlidingPanelMenuAdmin(admin.ModelAdmin):
    list_display = ('label','position',)
    list_display_links = ('label', 'position')

class VarieblesAdmin(admin.ModelAdmin):
    list_display = ('id','variable_name','description','client_name','value_class','active','writeable',)
    list_editable = ('active','writeable',)
    list_display_links = ('variable_name',)
    list_filter = ('client__short_name', 'active','writeable')
    search_fields = ['variable_name',]
    def client_name(self, instance):
        return instance.client.short_name

class WebClientControlItemAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
         context['adminform'].form.fields['variable'].queryset = Variable.objects.filter(writeable=1)
         return super(WebClientControlItemAdmin, self).render_change_form(request, context, args, kwargs)

class WebClientSlidingPanelMenuForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(WebClientSlidingPanelMenuForm, self).__init__(*args, **kwargs)
        wtf = WebClientControlItem.objects.all();
        w = self.fields['items'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.label+" (" + choice.get_type_display() + ")"))
        w.choices = choices

class WebClientSlidingPanelMenuAdmin(admin.ModelAdmin):
       # search_fields = ['variable_name',]
        filter_horizontal = ('items',)
        form = WebClientSlidingPanelMenuForm

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
admin.site.register(ClientConfig,ClientConfigAdmin)
admin.site.register(Variable,VarieblesAdmin)
admin.site.register(VariableConfigFileImport,VariableImportAdmin)
admin.site.register(WebClientChart,WebClientChartAdmin)
admin.site.register(WebClientPage)
admin.site.register(WebClientSlidingPanelMenu,WebClientSlidingPanelMenuAdmin)
admin.site.register(WebClientControlItem,WebClientControlItemAdmin)
admin.site.register(UnitConfig)
admin.site.register(ClientWriteTask,ClientWriteTaskAdmin)