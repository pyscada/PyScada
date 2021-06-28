# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceProtocol, DeviceHandler
from pyscada.models import Variable, VariableProperty
from pyscada.models import Scaling, Color
from pyscada.models import Unit
from pyscada.models import DeviceWriteTask, DeviceReadTask
from pyscada.models import Log
from pyscada.models import BackgroundProcess
from pyscada.models import ComplexEventGroup, ComplexEvent, ComplexEventItem
from pyscada.models import Event
from pyscada.models import RecordedEvent, RecordedData
from pyscada.models import Mail

from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import OneToOneRel

from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings

import datetime
import signal
import logging

logger = logging.getLogger(__name__)


# Custom AdminSite

class PyScadaAdminSite(AdminSite):
    site_header = 'PyScada Administration'


## admin actions
def restart_process(modeladmin, request, queryset):
    """
    restarts a dedicated process
    :return:
    """
    for process in queryset:
        process.restart()


restart_process.short_description = "Restart Processes"


def stop_process(modeladmin, request, queryset):
    """
    restarts a dedicated process
    :return:
    """
    for process in queryset:
        process.stop()


stop_process.short_description = "Terminate Processes"


def kill_process(modeladmin, request, queryset):
    """
    restarts a dedicated process
    :return:
    """
    for process in queryset:
        process.stop(signum=signal.SIGKILL)


kill_process.short_description = "Kill Processes"


## Custom Filters
class BackgroundProcessFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('parent process filter')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'parent_process'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        qs = model_admin.get_queryset(request)
        qs.filter(id__range=(1, 99))
        for item in qs:
            dp = DeviceProtocol.objects.filter(pk=item.id).first()
            if dp:
                yield (dp.pk, dp.app_name)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is not None:
            if int(self.value()) > 0:
                return queryset.filter(parent_process_id=self.value())


class VariableAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VariableAdminFrom, self).__init__(*args, **kwargs)
        if isinstance(self.instance, Variable):
            wtf = Color.objects.all()
            w = self.fields['chart_line_color'].widget
            color_choices = []
            for choice in wtf:
                color_choices.append((choice.id, choice.color_code()))
            w.choices = color_choices

            def create_option_color(self, name, value, label, selected, index, subindex=None, attrs=None):
                font_color = hex(int('ffffff', 16) - int(label[1::], 16))[2::]
                # attrs = self.build_attrs(attrs,{'style':'background: %s; color: #%s'%(label,font_color)})
                self.option_inherits_attrs = True
                return self._create_option(name, value, label, selected, index, subindex,
                                           attrs={'style': 'background: %s; color: #%s' % (label, font_color)})

            import types
            # from django.forms.widgets import Select
            w.widget._create_option = w.widget.create_option  # copy old method
            w.widget.create_option = types.MethodType(create_option_color, w.widget)  # replace old with new

    def has_changed(self):
        # Force save inline for the good protocol if selected device and protocol_id exists
        if self.data.get("device", None) != '':
            d = Device.objects.get(id=int(self.data.get("device", None)))
            if hasattr(self.instance, "protocol_id") and d is not None and \
                    d.protocol.id == self.instance.protocol_id:
                logger.error("Saving new inline for %s" % self.data.get('protocol', None))
                return True
        return super().has_changed()

    def clean(self):
        # on device change delete protocol variable that doesn't correspond
        if self.has_changed() and self.instance.pk and "device" in self.changed_data:
            related_variables = [field for field in Variable._meta.get_fields() if issubclass(type(field), OneToOneRel)]
            for v in related_variables:
                if hasattr(self.instance, v.name):
                    if getattr(self.instance, v.name).protocol_id != self.cleaned_data["device"].protocol.id:
                        getattr(self.instance, v.name).delete()


class VariableState(Variable):
    class Meta:
        proxy = True


class VariableStateAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_value')
    list_filter = ('device__short_name', 'active', 'unit__unit', 'value_class')
    list_display_links = ()
    list_per_page = 10
    actions = None
    search_fields = ('name',)
    form = VariableAdminFrom

    # Add inlines for any model with OneToOne relation with Device
    related_variables = [field for field in Variable._meta.get_fields() if issubclass(type(field), OneToOneRel)]
    inlines = []
    for v in related_variables:
        cl = type(v.name, (admin.StackedInline,), dict(model=v.related_model, form=VariableAdminFrom))  # classes=['collapse']
        inlines.append(cl)

    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.init.js',
            'pyscada/js/admin/display_inline_protocols_variable.js',
        )

    def last_value(self, instance):
        element = RecordedData.objects.last_element(variable_id=instance.pk)
        if element:
            return datetime.datetime.fromtimestamp(
                element.time_value()).strftime('%Y-%m-%d %H:%M:%S') \
                   + ' : ' + element.value().__str__() + ' ' + instance.unit.unit
        else:
            return ' - : NaN ' + instance.unit.unit


class DeviceForm(forms.ModelForm):
    def has_changed(self):
        # Force save inline for the good protocol if parent_device() and protocol_id exists
        if self.data.get('protocol', None) is not None:
            if hasattr(self.instance, "protocol_id") and \
                    self.data.get('protocol', None) == str(self.instance.protocol_id):
                logger.error("Saving new inline for %s" % self.data.get('protocol', None))
                return True
        else:
            if hasattr(self.instance, "protocol_id") and \
                    hasattr(self.instance, "parent_device") and \
                    self.instance.parent_device().protocol.id == self.instance.protocol_id:
                logger.error("Saving existing inline for %s" % self.instance.parent_device())
                return True
        return super().has_changed()


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'short_name', 'description', 'protocol', 'active', 'polling_interval')
    list_editable = ('active', 'polling_interval')
    list_display_links = ('short_name', 'description')
    save_as = True
    save_as_continue = True
    form = DeviceForm

    # Add inlines for any model with OneToOne relation with Device
    devices = [field for field in Device._meta.get_fields() if issubclass(type(field), OneToOneRel)]
    inlines = []
    for d in devices:
        cl = type(d.name, (admin.StackedInline,), dict(model=d.related_model, form=DeviceForm))  # classes=['collapse']
        inlines.append(cl)

    # List only activated protocols
    protocol_list = []
    if hasattr(settings, 'INSTALLED_APPS'):
        for app in settings.INSTALLED_APPS:
            if 'pyscada' in app:
                protocol_list.append(app.split(".")[1])

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "protocol":
            kwargs["queryset"] = DeviceProtocol.objects.filter(protocol__in=self.protocol_list)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Disable changing protocol
    def get_readonly_fields(self, request, obj=None):
        if obj is not None and obj.protocol is not None:
            return ['protocol']
        return []

    # Add JS file to display the right inline
    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.init.js',
            'pyscada/js/admin/display_inline_protocols_device.js',
        )


class VariableAdmin(admin.ModelAdmin):
    list_filter = ('device__short_name', 'active', 'writeable', 'unit__unit', 'value_class')
    search_fields = ['name', ]
    form = VariableAdminFrom
    save_as = True
    save_as_continue = True

    # Add inlines for any model with OneToOne relation with Device
    related_variables = [field for field in Variable._meta.get_fields() if issubclass(type(field), OneToOneRel)]
    inlines = []
    for v in related_variables:
        cl = type(v.name, (admin.StackedInline,), dict(model=v.related_model, form=VariableAdminFrom))  # classes=['collapse']
        inlines.append(cl)

    # Add JS file to display the right inline
    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.init.js',
            'pyscada/js/admin/display_inline_protocols_variable.js',
        )

    def device_name(self, instance):
        return instance.device.short_name

    def unit(self, instance):
        return instance.unit.unit


class CoreVariableAdmin(VariableAdmin):
    list_display = ('id', 'name', 'description', 'unit', 'scaling', 'device_name', 'value_class', 'active', 'writeable',)
    list_editable = ('active', 'writeable',)
    list_display_links = ('name',)


class DeviceWriteTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'user_name', 'start_time', 'done', 'failed',)
    # list_editable = ('active','writeable',)
    list_display_links = ('name',)
    list_filter = ('done', 'failed',)
    raw_id_fields = ('variable',)

    def name(self, instance):
        return instance.__str__()

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'

    def start_time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime('%Y-%m-%d %H:%M:%S')

    def has_delete_permission(self, request, obj=None):
        return True


class DeviceReadTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user_name', 'start_time', 'done', 'failed',)
    list_display_links = ('name',)
    list_filter = ('done', 'failed',)
    raw_id_fields = ('variable',)

    def name(self, instance):
        return instance.__str__()

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'

    def start_time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime('%Y-%m-%d %H:%M:%S')


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'level', 'message_short', 'user_name',)
    list_display_links = ('message_short',)
    list_filter = ('level', 'user')
    search_fields = ['message', ]

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return 'None'

    def time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BackgroundProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'pid', 'label', 'message', 'last_update', 'running_since', 'enabled', 'done', 'failed')
    list_filter = (BackgroundProcessFilter, 'enabled', 'done', 'failed')
    list_display_links = ('id', 'label', 'message')
    readonly_fields = ('message', 'last_update', 'running_since', 'done', 'failed')
    actions = [restart_process, stop_process, kill_process]


class RecordedEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'complex_event_group', 'time_begin', 'time_end', 'active',)
    list_display_links = ('event', 'complex_event_group',)
    list_filter = ('event', 'active')
    readonly_fields = ('time_begin', 'time_end',)


class MailAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'message', 'html_message', 'last_update', 'done', 'send_fail_count',)
    list_display_links = ('subject',)
    list_filter = ('done',)

    def last_update(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime('%Y-%m-%d %H:%M:%S')


class ComplexEventAdminInline(admin.TabularInline):
    model = ComplexEvent
    extra = 0
    show_change_link = True
    readonly_fields = ('active',)


class ComplexEventItemAdminInline(admin.StackedInline):
    model = ComplexEventItem
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('fixed_limit_low', 'variable_limit_low', 'limit_low_type', 'hysteresis_low',),
                       ('variable', 'variable_property',),
                       ('fixed_limit_high', 'variable_limit_high', 'limit_high_type', 'hysteresis_high',)),
        },),
    )
    raw_id_fields = ('variable', 'variable_limit_low', 'variable_limit_high',)


class ComplexEventGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'variable_to_change', 'default_send_mail', 'default_value', 'last_level',)
    list_display_links = ('id', 'label',)
    list_filter = ('variable_to_change', 'default_send_mail', 'default_value',)
    filter_horizontal = ('complex_mail_recipients',)
    inlines = [ComplexEventAdminInline]
    raw_id_fields = ('variable_to_change',)
    readonly_fields = ('last_level',)
    save_as = True
    save_as_continue = True


class ComplexEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'level', 'send_mail', 'new_value', 'complex_event_group', 'order', 'active',)
    list_display_links = ('id',)
    list_filter = ('complex_event_group__label', 'level', 'send_mail',)
    inlines = [ComplexEventItemAdminInline]
    readonly_fields = ('active',)
    save_as = True
    save_as_continue = True


class ComplexEventItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'fixed_limit_low', 'variable_limit_low', 'limit_low_type', 'hysteresis_low', 'variable',
                    'fixed_limit_high', 'variable_limit_high', 'limit_high_type', 'hysteresis_high',)
    list_display_links = ('id',)
    list_filter = ('variable',)

    raw_id_fields = ('variable',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'variable', 'limit_type', 'level', 'action',)
    list_display_links = ('id', 'label',)
    list_filter = ('level', 'limit_type', 'action',)
    filter_horizontal = ('mail_recipients',)

    raw_id_fields = ('variable',)


class VariablePropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'variable', 'name', 'property_class', 'value', 'timestamp')
    list_display_links = ('id', 'variable', 'name', 'property_class')
    list_filter = ('variable', 'name', 'property_class',)
    raw_id_fields = ('variable',)
    save_as = True
    save_as_continue = True

    def value(self, instance):
        return instance.value()


admin_site = PyScadaAdminSite(name='pyscada_admin')
admin_site.register(Device, DeviceAdmin)
admin_site.register(DeviceHandler)
admin_site.register(Variable, CoreVariableAdmin)
admin_site.register(VariableProperty, VariablePropertyAdmin)
admin_site.register(Scaling)
admin_site.register(Unit)
admin_site.register(ComplexEventGroup, ComplexEventGroupAdmin)
admin_site.register(ComplexEvent, ComplexEventAdmin)
admin_site.register(Event, EventAdmin)
admin_site.register(RecordedEvent, RecordedEventAdmin)
admin_site.register(Mail, MailAdmin)
admin_site.register(DeviceWriteTask, DeviceWriteTaskAdmin)
admin_site.register(DeviceReadTask, DeviceReadTaskAdmin)
admin_site.register(Log, LogAdmin)
admin_site.register(BackgroundProcess, BackgroundProcessAdmin)
admin_site.register(VariableState, VariableStateAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
