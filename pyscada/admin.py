# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.models import Device, DeviceProtocol, DeviceHandler
from pyscada.models import Variable, VariableProperty, DataSource, DataSourceModel
from pyscada.models import Scaling, Color
from pyscada.models import Unit, Dictionary, DictionaryItem
from pyscada.models import DeviceWriteTask, DeviceReadTask
from pyscada.models import Log
from pyscada.models import BackgroundProcess
from pyscada.models import (
    ComplexEvent,
    ComplexEventLevel,
    ComplexEventInput,
    ComplexEventOutput,
)
from pyscada.models import Event
from pyscada.models import RecordedEvent, RecordedData
from pyscada.models import Mail

from django.contrib import messages
from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.related import OneToOneRel

from django import forms
from django.db.utils import ProgrammingError, OperationalError
from django.conf import settings

import datetime
import signal
import logging

logger = logging.getLogger(__name__)


# Custom AdminSite


class PyScadaAdminSite(AdminSite):
    site_header = "PyScada Administration"


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


def silent_delete(self, request, queryset):
    queryset.delete()


silent_delete.short_description = "Silent delete (lot of records)"


# Custom Filters
class BackgroundProcessFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("parent process filter")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "parent_process"

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


# Admin models
class VariableAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VariableAdminFrom, self).__init__(*args, **kwargs)

        # disable delete button for datasource foreign key
        if "datasource" in self.fields:
            self.fields["datasource"].widget.can_delete_related = False

        if isinstance(self.instance, Variable):
            wtf = Color.objects.all()
            if "chart_line_color" in self.fields:
                w = self.fields["chart_line_color"].widget
                color_choices = []
                for choice in wtf:
                    color_choices.append((choice.id, choice.color_code()))
                w.choices = color_choices

                def create_option_color(
                    self, name, value, label, selected, index, subindex=None, attrs=None
                ):
                    font_color = hex(int("ffffff", 16) - int(label[1::], 16))[2::]
                    # attrs = self.build_attrs(attrs,{'style':'background: %s; color: #%s'%(label,font_color)})
                    self.option_inherits_attrs = True
                    return self._create_option(
                        name,
                        value,
                        label,
                        selected,
                        index,
                        subindex,
                        attrs={
                            "style": "background: %s; color: #%s" % (label, font_color)
                        },
                    )

                import types

                # from django.forms.widgets import Select
                w.widget._create_option = w.widget.create_option  # copy old method
                w.widget.create_option = types.MethodType(
                    create_option_color, w.widget
                )  # replace old with new

    def has_changed(self):
        # Force save inline for the good protocol if selected device and protocol_id exists
        # todo : try it with all the protocol, it seems to be not working
        if (
            self.data.get("device", None) != ""
            and self.data.get("device", None) is not None
        ):
            d = Device.objects.get(id=int(self.data.get("device", None)))
            if (
                hasattr(self.instance, "protocol_id")
                and d is not None
                and d.protocol.id == self.instance.protocol_id
            ):
                return True
        return super().has_changed()

    def clean(self):
        super().clean()
        # on device change, delete protocol variable that doesn't correspond
        if self.has_changed() and self.instance.pk and "device" in self.changed_data:
            related_variables = [
                field
                for field in Variable._meta.get_fields()
                if issubclass(type(field), OneToOneRel)
            ]
            for v in related_variables:
                if (
                    hasattr(self.instance, v.name)
                    and hasattr(self, "device")
                    and getattr(self.instance, v.name).protocol_id
                    != self.cleaned_data["device"].protocol.id
                ):
                    getattr(self.instance, v.name).delete()


class VariableState(Variable):
    class Meta:
        proxy = True


class VariableStateAdmin(admin.ModelAdmin):
    list_display = ("name", "last_value")
    list_filter = ("device__short_name", "active", "unit__unit", "value_class")
    list_display_links = ()
    list_per_page = 10
    actions = [silent_delete]
    search_fields = ("name",)
    form = VariableAdminFrom

    # Add inlines for any model with OneToOne relation with Device
    related_variables = [
        field
        for field in Variable._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    inlines = []
    for v in related_variables:
        cl = type(
            v.name,
            (admin.StackedInline,),
            dict(model=v.related_model, form=VariableAdminFrom),
        )  # classes=['collapse']
        inlines.append(cl)

    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/jquery.init.js",
            "pyscada/js/admin/display_inline_protocols_variable.js",
        )

    def last_value(self, instance):
        try:
            v = Variable.objects.get(id=instance.pk)
            if v.query_prev_value(timeout=10):
                try:
                    return f"{datetime.datetime.fromtimestamp(v.timestamp_old).strftime('%Y-%m-%d %H:%M:%S')} : {v.prev_value.__str__()} {instance.unit.unit}"
                except ValueError as e:
                    return f"ValueError {e} - with timestamp {v.timestamp_old} : {v.prev_value.__str__()} {instance.unit.unit}"
        except Variable.DoesNotExist:
            return "Variable does not exist"
        except TimeoutError:
            return "Timeout on value query"
        return f" - : NaN {instance.unit.unit}"


class DeviceForm(forms.ModelForm):
    def has_changed(self):
        # Force save inline for the right protocol if parent_device() and protocol_id exists
        if self.data.get("protocol", None) is not None:
            if hasattr(self.instance, "protocol_id") and self.data.get(
                "protocol", None
            ) == str(self.instance.protocol_id):
                return True
        else:
            if (
                hasattr(self.instance, "protocol_id")
                and hasattr(self.instance, "parent_device")
                and self.instance.parent_device() is not None
                and self.instance.parent_device().protocol is not None
                and self.instance.parent_device().protocol.id
                == self.instance.protocol_id
            ):
                return True
        return super().has_changed()


class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "short_name",
        "description",
        "protocol",
        "active",
        "polling_interval",
        "instrument_handler",
    )
    list_editable = ("active", "polling_interval", "instrument_handler")
    list_display_links = (
        "short_name",
        "description",
    )
    list_filter = (
        "protocol",
        "active",
        "polling_interval",
    )
    actions = [silent_delete]
    save_as = True
    save_as_continue = True
    form = DeviceForm

    # Add inlines for any model with OneToOne relation with Device
    devices = [
        field
        for field in Device._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    inlines = []
    for d in devices:
        device_dict = dict(model=d.related_model, form=DeviceForm)
        if hasattr(d.related_model, "fk_name"):
            device_dict["fk_name"] = d.related_model.fk_name
        if hasattr(d.related_model, "FormSet"):
            device_dict["formset"] = d.related_model.FormSet
        if hasattr(d.related_model, "fieldsets"):
            device_dict["fieldsets"] = d.related_model.fieldsets
        if hasattr(d.related_model, "filter_horizontal"):
            device_dict["filter_horizontal"] = d.related_model.filter_horizontal
        if hasattr(d.related_model, "filter_vertical"):
            device_dict["filter_vertical"] = d.related_model.filter_vertical
        # if hasattr(d.related_model, "formfield_for_foreignkey"):
        #    device_dict["formfield_for_foreignkey"] = d.related_model.formfield_for_foreignkey
        cl = type(d.name, (admin.StackedInline,), device_dict)  # classes=['collapse']
        inlines.append(cl)

    # List only activated protocols
    protocol_list = list()
    protocol_list.append("generic")
    if hasattr(settings, "INSTALLED_APPS"):
        try:
            for protocol in DeviceProtocol.objects.filter(
                app_name__in=settings.INSTALLED_APPS
            ):
                protocol_list.append(protocol.protocol)
        except (ProgrammingError, OperationalError) as e:
            logger.debug(e)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # For new device, show all the protocols from the installed apps in settings.py
        # For existing device, show only the selected protocol to avoid changing
        if db_field.name == "protocol":
            if (
                "object_id" in request.resolver_match.kwargs
                and Device.objects.get(id=request.resolver_match.kwargs["object_id"])
                is not None
                and Device.objects.get(
                    id=request.resolver_match.kwargs["object_id"]
                ).protocol
            ):
                kwargs["queryset"] = DeviceProtocol.objects.filter(
                    protocol__in=[
                        Device.objects.get(
                            id=request.resolver_match.kwargs["object_id"]
                        ).protocol.protocol,
                    ]
                )
            else:
                kwargs["queryset"] = DeviceProtocol.objects.filter(
                    protocol__in=self.protocol_list
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Add JS file to display the right inline and to hide/show fields
    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/jquery.init.js",
            "pyscada/js/admin/display_inline_protocols_device.js",
            "pyscada/js/admin/hideshow.js",
        )


class DeviceHandlerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "handler_class",
        "handler_path",
    )
    list_editable = (
        "handler_class",
        "handler_path",
    )
    list_display_links = ("name",)
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


class VariableAdmin(admin.ModelAdmin):
    list_filter = (
        "device__protocol",
        "device",
        "active",
        "writeable",
        "unit__unit",
        "value_class",
        "scaling",
    )
    search_fields = [
        "name",
    ]
    list_per_page = 10
    form = VariableAdminFrom
    save_as = True
    save_as_continue = True

    # Add inlines for any model with OneToOne relation with Device
    related_variables = [
        field
        for field in Variable._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    inlines = []
    for v in related_variables:
        variable_dict = dict(model=v.related_model, form=VariableAdminFrom)
        if hasattr(v.related_model, "fk_name"):
            variable_dict["fk_name"] = v.related_model.fk_name
        if hasattr(v.related_model, "FormSet"):
            variable_dict["formset"] = v.related_model.FormSet
        if hasattr(v.related_model, "fieldsets"):
            variable_dict["fieldsets"] = v.related_model.fieldsets
        cl = type(v.name, (admin.StackedInline,), variable_dict)  # classes=['collapse']
        inlines.append(cl)

    # Add JS file to display the right inline
    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/jquery.init.js",
            "pyscada/js/admin/display_inline_protocols_variable.js",
            "pyscada/js/admin/hideshow.js",
        )

    def device_name(self, instance):
        return instance.device.short_name

    def unit(self, instance):
        return instance.unit.unit

    def color_code(self, instance):
        return instance.chart_line_color.color_code()


class CoreVariableAdmin(VariableAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "unit",
        "scaling",
        "device",
        "value_class",
        "active",
        "writeable",
        "dictionary",
    )
    list_editable = (
        "active",
        "writeable",
        "unit",
        "scaling",
        "dictionary",
    )
    list_display_links = ("name",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # show only datasource with can_select as True
        if db_field.name == "datasource":
            ids = []
            for d in DataSource.objects.all():
                if d.datasource_model.can_select:
                    ids.append(d.id)
            kwargs["queryset"] = DataSource.objects.filter(id__in=ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ScalingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "description",
        "input_low",
        "input_high",
        "output_low",
        "output_high",
        "limit_input",
    )
    list_editable = (
        "input_low",
        "input_high",
        "output_low",
        "output_high",
        "limit_input",
    )
    list_display_links = ("description",)
    save_as = True
    save_as_continue = True


class DeviceWriteTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "value",
        "user_name",
        "start_time",
        "done",
        "failed",
    )
    # list_editable = ('active','writeable',)
    list_display_links = ("name",)
    list_filter = (
        "done",
        "failed",
    )
    raw_id_fields = ("variable",)
    save_as = True
    save_as_continue = True

    def name(self, instance):
        return instance.__str__()

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return "None"

    def start_time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def has_delete_permission(self, request, obj=None):
        return True


class DeviceReadTaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "user_name",
        "start_time",
        "done",
        "failed",
    )
    list_display_links = ("name",)
    list_filter = (
        "done",
        "failed",
    )
    raw_id_fields = ("variable",)
    save_as = True
    save_as_continue = True

    def name(self, instance):
        return instance.__str__()

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return "None"

    def start_time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.start)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class LogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "time",
        "level",
        "message_short",
        "user_name",
    )
    list_display_links = ("message_short",)
    list_filter = ("level", "user")
    search_fields = [
        "message",
    ]

    def user_name(self, instance):
        try:
            return instance.user.username
        except:
            return "None"

    def time(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BackgroundProcessAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pid",
        "label",
        "message",
        "last_update",
        "running_since",
        "enabled",
        "done",
        "failed",
    )
    list_filter = (BackgroundProcessFilter, "enabled", "done", "failed")
    list_display_links = ("id", "label", "message")
    readonly_fields = ("message", "last_update", "running_since", "done", "failed")
    actions = [restart_process, stop_process, kill_process]


class RecordedEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "event",
        "complex_event",
        "time_begin",
        "time_end",
        "active",
    )
    list_display_links = (
        "event",
        "complex_event",
    )
    list_filter = ("event", "active")
    readonly_fields = (
        "time_begin",
        "time_end",
    )
    save_as = True
    save_as_continue = True


class MailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "message",
        "html_message",
        "last_update",
        "done",
        "send_fail_count",
    )
    list_display_links = ("subject",)
    list_filter = ("done",)

    def last_update(self, instance):
        return datetime.datetime.fromtimestamp(int(instance.timestamp)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )


class ComplexEventOutputAdminInline(admin.TabularInline):
    model = ComplexEventOutput
    extra = 0
    show_change_link = False
    fields = ("variable", "value")


class ComplexEventLevelAdminInline(admin.TabularInline):
    model = ComplexEventLevel
    extra = 0
    show_change_link = True
    readonly_fields = ("active",)


class ComplexEventInputAdminInline(admin.StackedInline):
    model = ComplexEventInput
    extra = 0
    fieldsets = (
        (
            None,
            {
                "fields": (
                    (
                        "fixed_limit_low",
                        "variable_limit_low",
                        "limit_low_type",
                        "hysteresis_low",
                    ),
                    (
                        "variable",
                        "variable_property",
                    ),
                    (
                        "fixed_limit_high",
                        "variable_limit_high",
                        "limit_high_type",
                        "hysteresis_high",
                    ),
                ),
            },
        ),
    )
    raw_id_fields = (
        "variable",
        "variable_limit_low",
        "variable_limit_high",
    )


class ComplexEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "label",
        "default_send_mail",
        "last_level",
    )
    list_display_links = (
        "id",
        "label",
    )
    list_filter = ("default_send_mail",)
    filter_horizontal = ("complex_mail_recipients",)
    inlines = [ComplexEventLevelAdminInline, ComplexEventOutputAdminInline]
    readonly_fields = ("last_level",)
    save_as = True
    save_as_continue = True


class ComplexEventLevelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "level",
        "send_mail",
        "complex_event",
        "order",
        "active",
    )
    list_display_links = ("id",)
    list_filter = (
        "complex_event__label",
        "level",
        "send_mail",
    )
    inlines = [ComplexEventInputAdminInline, ComplexEventOutputAdminInline]
    readonly_fields = ("active",)
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


class ComplexEventInputAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "fixed_limit_low",
        "variable_limit_low",
        "limit_low_type",
        "hysteresis_low",
        "variable",
        "fixed_limit_high",
        "variable_limit_high",
        "limit_high_type",
        "hysteresis_high",
    )
    list_display_links = ("id",)
    list_filter = ("variable",)
    save_as = True
    save_as_continue = True
    raw_id_fields = ("variable",)


class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "label",
        "variable",
        "limit_type",
        "level",
        "action",
    )
    list_display_links = (
        "id",
        "label",
    )
    list_filter = (
        "level",
        "limit_type",
        "action",
    )
    filter_horizontal = ("mail_recipients",)
    save_as = True
    save_as_continue = True
    raw_id_fields = ("variable",)


class VariablePropertyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "variable",
        "name",
        "property_class",
        "value",
        "timestamp",
        "last_modified",
    )
    list_display_links = ("id", "variable", "name", "property_class")
    list_filter = (
        "variable",
        "name",
        "property_class",
    )
    raw_id_fields = ("variable",)
    readonly_fields = ["last_modified"]
    save_as = True
    save_as_continue = True

    def value(self, instance):
        return instance.value()


class DictionaryItemInline(admin.TabularInline):
    model = DictionaryItem
    extra = 1


class DictionaryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_filter = ("variable",)
    save_as = True
    save_as_continue = True
    inlines = [DictionaryItemInline]

    def has_module_permission(self, request):
        return False


class DataSourceModelSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value:
            option["attrs"][
                "data-inline-datasource-model-name"
            ] = value.instance.inline_model_name

        return option


class DataSourceAdminChangeForm(forms.ModelForm):
    class Meta:
        model = DataSource
        fields = "__all__"
        widgets = {"datasource_model": DataSourceModelSelect}


class DataSourceAdminAddForm(forms.ModelForm):
    class Meta:
        model = DataSource
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        wtf = DataSourceModel.objects.all()
        super().__init__(*args, **kwargs)
        w = self.fields["datasource_model"].widget

        datasource_choices = []
        for choice in wtf:
            if choice.can_add:
                datasource_choices.append((choice.id, choice.__str__()))
        w.choices = datasource_choices

        def create_option_datasource(
            self, name, value, label, selected, index, subindex=None, attrs=None
        ):
            inline_datasource_model_name = DataSourceModel.objects.get(
                id=value
            ).inline_model_name
            self.option_inherits_attrs = True
            return self._create_option(
                name,
                value,
                label,
                selected,
                index,
                subindex,
                attrs={
                    "data-inline-datasource-model-name": inline_datasource_model_name,
                },
            )

        import types

        # from django.forms.widgets import Select
        w._create_option = w.create_option  # copy old method
        w.create_option = types.MethodType(
            create_option_datasource, w
        )  # replace old with new


class DataSourceAdmin(admin.ModelAdmin):
    list_display = (
        "datasource_model",
        "datasource_name",
    )

    form = DataSourceAdminChangeForm

    # Add inlines for any model with OneToOne relation with Device
    items = [
        field
        for field in DataSource._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    inlines = []
    for item in items:
        items_dict = dict(model=item.related_model)
        if hasattr(item.related_model, "fk_name"):
            items_dict["fk_name"] = item.related_model.fk_name
        if hasattr(item.related_model, "FormSet"):
            items_dict["formset"] = item.related_model.FormSet
        if hasattr(item.related_model, "fieldsets"):
            items_dict["fieldsets"] = item.related_model.fieldsets
        if hasattr(item.related_model, "Form"):
            items_dict["form"] = item.related_model.Form
        # if hasattr(d.related_model, "formfield_for_foreignkey"):
        #    items_dict["formfield_for_foreignkey"] = d.related_model.formfield_for_foreignkey
        cl = type(item.name, (admin.StackedInline,), items_dict)  # classes=['collapse']
        inlines.append(cl)

    # Add JS file to display the right inline and to hide/show fields
    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            "pyscada/js/admin/display_inline_datasource.js",
        )

    def get_form(self, request, obj=None, change=None, **kwargs):
        if not obj:
            # Use a different form only when adding a new record
            return DataSourceAdminAddForm

        return super().get_form(request, obj=obj, change=change, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        # disable all the of an inline if the data source model can_change field is false
        def get_formset(self, request, obj=None, **kwargs):
            formset = self.get_formset(request, obj=None, **kwargs)
            for field in formset.form.base_fields:
                if not obj.datasource_model.can_change:
                    formset.form.base_fields[field].disabled = True
            return formset

        for inline in self.get_inline_instances(request, obj):
            if obj is not None:
                yield get_formset(inline, request, obj), inline
            else:
                yield inline.get_formset(request, obj), inline

    def datasource_name(self, obj):
        return obj.__str__()

    def get_deleted_objects(self, objs, request):
        # Not allow to delete the data source with id = 1
        new_objs = list()
        for obj in objs:
            if obj.id != 1:
                new_objs.append(obj.get_related_datasource())
        (
            deleted_objects,
            model_count,
            perms_needed,
            protected,
        ) = super().get_deleted_objects(objs, request)
        return deleted_objects, model_count, perms_needed, protected

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.id == 1:
            messages.error(request, f"You cannot delete the {obj} !")
            return False
        return super().has_delete_permission(request, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # For new data source, show all the data source models
        # For existing data source, show only the selected data source model to avoid changing
        if db_field.name == "datasource_model":
            if (
                "object_id" in request.resolver_match.kwargs
                and DataSource.objects.get(
                    id=request.resolver_match.kwargs["object_id"]
                )
                is not None
                and DataSource.objects.get(
                    id=request.resolver_match.kwargs["object_id"]
                ).datasource_model
            ):
                kwargs["queryset"] = DataSourceModel.objects.filter(
                    id=DataSource.objects.get(
                        id=request.resolver_match.kwargs["object_id"]
                    ).datasource_model.id,
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin_site = PyScadaAdminSite(name="pyscada_admin")
admin_site.register(Device, DeviceAdmin)
admin_site.register(DeviceHandler, DeviceHandlerAdmin)
admin_site.register(Variable, CoreVariableAdmin)
admin_site.register(VariableProperty, VariablePropertyAdmin)
admin_site.register(Scaling, ScalingAdmin)
admin_site.register(Unit)
admin_site.register(ComplexEvent, ComplexEventAdmin)
admin_site.register(ComplexEventLevel, ComplexEventLevelAdmin)
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
admin_site.register(Dictionary, DictionaryAdmin)
admin_site.register(DataSource, DataSourceAdmin)
# admin_site.register(DataSourceModel)
