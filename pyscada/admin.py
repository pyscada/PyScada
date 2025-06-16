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
from pyscada.models import DeviceHandlerParameter, VariableHandlerParameter

from django.contrib import messages
from django.contrib import admin
from django import forms
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.related import OneToOneRel
from django.utils.html import mark_safe
from django.forms import BaseInlineFormSet
from django.core.exceptions import ValidationError

from django import forms
from django.db.utils import ProgrammingError, OperationalError
from django.conf import settings

import sys
import datetime
import signal
import logging

logger = logging.getLogger(__name__)


# Custom AdminSite


class PyScadaAdminSite(AdminSite):
    site_header = "PyScada Administration"


def populate_inline(items, form_model=None, output=[], stacked=admin.StackedInline):
    for item in items:
        if form_model is None:
            item_dict = dict(model=item.related_model)
        else:
            item_dict = dict(model=item.related_model, form=form_model)
        if hasattr(item.related_model, "fk_name"):
            item_dict["fk_name"] = item.related_model.fk_name
        if hasattr(item.related_model, "FormSet"):
            item_dict["formset"] = item.related_model.FormSet
        if hasattr(item.related_model, "fieldsets"):
            item_dict["fieldsets"] = item.related_model.fieldsets
        if hasattr(item.related_model, "filter_horizontal"):
            item_dict["filter_horizontal"] = item.related_model.filter_horizontal
        if hasattr(item.related_model, "filter_vertical"):
            item_dict["filter_vertical"] = item.related_model.filter_vertical
        if hasattr(item.related_model, "Form"):
            items_dict["form"] = item.related_model.Form
        # if hasattr(item.related_model, "formfield_for_foreignkey"):
        #    item_dict["formfield_for_foreignkey"] = item.related_model.formfield_for_foreignkey
        out = type(item.name, (stacked,), item_dict)  # classes=['collapse']
        output.append(out)
    return output


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
class VariableInlineAdminFrom(forms.ModelForm):
    def has_changed(self):
        # Force save inline for the good protocol if selected device and protocol_id exists
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
        return False


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
                w.widget.attrs = {
                    "onchange": "this.style.backgroundColor=this.options[this.selectedIndex].style."
                    "backgroundColor;this.style.color=this.options[this.selectedIndex].style.color"
                }


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
    inlines = populate_inline(
        related_variables,
        VariableInlineAdminFrom,
        output=[],
        stacked=admin.StackedInline,
    )

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


class DeviceHandlerParameterInlineForm(forms.ModelForm):
    class Meta:
        model = DeviceHandlerParameter
        fields = ("value",)


class DeviceHandlerParameterInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        raise_error = []
        if self.instance.instrument_handler is not None:
            parameters = self.instance.instrument_handler.get_device_parameters()
        else:
            parameters = {}
        for parameter in parameters:
            parameters[parameter]["found"] = False
        result_forms = []
        for form in self.forms:
            if form.instance.name in parameters.keys():
                if parameters[form.instance.name]["found"]:
                    # DeviceHandlerParameter already found, delete duplicate
                    form.instance.delete()
                else:
                    parameters[form.instance.name]["found"] = True
                    if (
                        not parameters[form.instance.name].get("null", True)
                        and form.instance.value == ""
                    ):
                        # value is needed
                        raise_error.append(form.instance.name)
                result_forms.append(form)
            else:
                # DeviceHandlerParameter not needed
                try:
                    form.instance.delete()
                except ValueError:
                    pass
        self.forms = result_forms
        # TODO : redirect to a specific page if parameters was missing on the add/change page, in order to create these parameters
        if len(raise_error):
            raise ValidationError(
                f"Value is required for parameters {','.join([str(x) for x in raise_error])}"
            )


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
    inlines = populate_inline(
        devices, DeviceForm, output=[], stacked=admin.StackedInline
    )

    item_dict = dict(
        model=DeviceHandlerParameter,
        max_num=0,
        can_delete=False,
        formset=DeviceHandlerParameterInlineFormSet,
        form=DeviceHandlerParameterInlineForm,
    )
    inlines.append(type("DeviceHandlerParameter", (admin.StackedInline,), item_dict))

    def get_form(self, request, obj=None, **kwargs):
        if (
            kwargs.get("fields", False)
            and "instrument_handler" in kwargs["fields"]
            and obj is None
        ):
            help_texts = kwargs.get("help_texts", {})
            help_texts.update(
                {
                    "instrument_handler": "If the handler needs specific configuration, save the device and you will add the config next."
                }
            )
            kwargs.update({"help_texts": help_texts})
        return super().get_form(request, obj, **kwargs)

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

                kwargs["queryset"] = DeviceProtocol.objects.filter(
                    protocol__in=protocol_list
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
        "found",
    )
    list_editable = (
        "handler_class",
        "handler_path",
    )
    list_display_links = ("name",)
    save_as = True
    save_as_continue = True
    readonly_fields = [
        "content",
    ]

    def has_module_permission(self, request):
        return False

    @admin.display(boolean=True)
    def found(self, instance):
        try:
            if instance.handler_path is not None:
                sys.path.append(instance.handler_path)
            mod = __import__(instance.handler_class, fromlist=["Handler"])
            return True
        except ModuleNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Handler {self} failed to be found : {e}")
            return False

    def content(self, instance):
        try:
            if instance.handler_path is not None:
                sys.path.append(instance.handler_path)
            if instance.handler_class in sys.modules:
                del sys.modules[instance.handler_class]
            mod = __import__(instance.handler_class, fromlist=["Handler"])
            if hasattr(mod, "pyscada_admin_content"):
                return mark_safe(getattr(mod, "pyscada_admin_content"))
            with open(mod.__file__) as f:
                return f.read()
        except ModuleNotFoundError:
            return "Handler file not found."
        except Exception as e:
            return f"Handler reading failed : {e}"

    def get_form(self, request, obj=None, **kwargs):
        if kwargs.get("fields", False) and "content" in kwargs["fields"]:
            help_texts = kwargs.get("help_texts", {})
            help_texts.update(
                {
                    "content": "Return the content of 'pyscada_admin_content' variable if defined in the handler file, otherwise return the whole file content."
                }
            )
            kwargs.update({"help_texts": help_texts})
        return super().get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if obj == None:
            return []
        return super().get_readonly_fields(request, obj)

    class Media:
        js = (
            # show the contet as preformatted code
            "pyscada/js/admin/handler_content_as_pre.js",
        )


class VariableHandlerParameterInlineForm(forms.ModelForm):
    class Meta:
        model = VariableHandlerParameter
        fields = ("value",)


class VariableHandlerParameterInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        raise_error = []
        if self.instance.device.instrument_handler is not None:
            parameters = self.instance.device.instrument_handler.get_variable_parameters()
        else:
            parameters = {}
        for parameter in parameters:
            parameters[parameter]["found"] = False
        result_forms = []
        for form in self.forms:
            if form.instance.name in parameters.keys():
                if parameters[form.instance.name]["found"]:
                    # VariableHandlerParameter already found, delete duplicate
                    form.instance.delete()
                else:
                    parameters[form.instance.name]["found"] = True
                    if (
                        not parameters[form.instance.name].get("null", True)
                        and form.instance.value == None
                    ):
                        # value is needed
                        raise_error.append(form.instance.name)
                result_forms.append(form)
            else:
                # VariableHandlerParameter not needed
                try:
                    form.instance.delete()
                except ValueError:
                    pass
            # your custom formset validation
        self.forms = result_forms
        # TODO : redirect to a specific page if parameters was missing on the add/change page, in order to create these parameters
        if len(raise_error):
            raise ValidationError(
                f"Value is required for parameters {','.join([str(x) for x in raise_error])}"
            )


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
    inlines = populate_inline(
        related_variables,
        VariableInlineAdminFrom,
        output=[],
        stacked=admin.StackedInline,
    )
    item_dict = dict(
        model=VariableHandlerParameter,
        max_num=0,
        can_delete=False,
        formset=VariableHandlerParameterInlineFormSet,
        form=VariableHandlerParameterInlineForm,
    )
    inlines.append(type("VariableHandlerParameter", (admin.StackedInline,), item_dict))

    def get_form(self, request, obj=None, **kwargs):
        if kwargs.get("fields", False) and "device" in kwargs["fields"] and obj is None:
            help_texts = kwargs.get("help_texts", {})
            help_texts.update(
                {
                    "device": "If the device handler needs specific configuration, save the variable and you will add the config next."
                }
            )
            kwargs.update({"help_texts": help_texts})
        return super().get_form(request, obj, **kwargs)

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
    inlines = populate_inline(items, None, output=[], stacked=admin.StackedInline)

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
