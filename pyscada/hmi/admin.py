# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pyscada.admin import admin_site

from pyscada.models import Variable
from pyscada.models import Color
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Chart, ChartAxis
from pyscada.hmi.models import Form
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import Page
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import (
    DisplayValueOption,
    ControlElementOption,
    DisplayValueColorOption,
    DisplayValueOptionTemplate,
)
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.hmi.models import ProcessFlowDiagramItem
from pyscada.hmi.models import Pie
from pyscada.hmi.models import Theme
from pyscada.hmi.models import CssClass
from pyscada.hmi.models import TransformData

from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django import forms
from django.db.models.fields.related import OneToOneRel
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateDoesNotExist, TemplateSyntaxError
from django.template.loader import get_template

import logging

logger = logging.getLogger(__name__)


class FormListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("form filter")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "form"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        result = list()
        for form in Form.objects.all():
            result.append(
                (form.pk, form.title),
            )
        return result

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() is not None:
            return queryset.filter(control_items_form__in=self.value())


class ChartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChartForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all()
        w = self.fields["variables"].widget
        choices = []
        for choice in wtf:
            choices.append(
                (choice.id, choice.name + "( " + choice.unit.description + " )")
            )
        w.choices = choices


class ChartAxisInline(admin.TabularInline):
    model = ChartAxis
    filter_vertical = ["variables"]

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1


class ChartAdmin(admin.ModelAdmin):
    list_per_page = 100
    # ordering = ['position',]
    search_fields = [
        "title",
    ]
    List_display_link = ("title",)
    list_display = (
        "id",
        "title",
        "x_axis_label",
        "x_axis_linlog",
    )
    # list_filter = ('widget__page__title', 'widget__title',)
    # form = ChartForm
    save_as = True
    save_as_continue = True
    inlines = [ChartAxisInline]

    def name(self, instance):
        return instance.variables.name

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "x_axis_var":
            kwargs["empty_label"] = "Time series"
        return super(ChartAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


class PieForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PieForm, self).__init__(*args, **kwargs)
        wtf = Variable.objects.all()
        w = self.fields["variables"].widget
        choices = []
        for choice in wtf:
            choices.append(
                (choice.id, choice.name + "( " + choice.unit.description + " )")
            )
        w.choices = choices


class PieAdmin(admin.ModelAdmin):
    list_per_page = 100
    # ordering = ['position',]
    search_fields = [
        "name",
    ]
    filter_horizontal = ("variables", "variable_properties")
    List_display_link = ("title",)
    list_display = ("id", "title")
    form = PieForm
    save_as = True
    save_as_continue = True

    def name(self, instance):
        return instance.variables.name


class FormAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "control_items",
        "hidden_control_items_to_true",
    )
    list_filter = ("controlpanel",)
    save_as = True
    save_as_continue = True


class DisplayValueOptionAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisplayValueOptionAdminFrom, self).__init__(*args, **kwargs)
        wtf = Color.objects.all()
        w = self.fields["color"].widget
        color_choices = [(None, None)]
        for choice in wtf:
            color_choices.append((choice.id, choice.color_code()))
        w.choices = color_choices

        def create_option_color(
            self, name, value, label, selected, index, subindex=None, attrs=None
        ):
            if label is None:
                return self._create_option(
                    name, value, label, selected, index, subindex, attrs=None
                )
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
                attrs={"style": "background: %s; color: #%s" % (label, font_color)},
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

    def clean(self):
        super().clean()
        color_options = set()

        if self.data.get("gradient", False) == "on":
            for d in self.data:
                if (
                    "displayvaluecoloroption_set-" in d
                    and d[
                        len("displayvaluecoloroption_set-") : len(
                            "displayvaluecoloroption_set-"
                        )
                        + 1
                    ].isdigit()
                    and "displayvaluecoloroption_set-"
                    + d[
                        len("displayvaluecoloroption_set-") : len(
                            "displayvaluecoloroption_set-"
                        )
                        + 1
                    ]
                    + "-DELETE"
                    not in self.data
                ):
                    color_options.update(
                        d[
                            len("displayvaluecoloroption_set-") : len(
                                "displayvaluecoloroption_set-"
                            )
                            + 1
                        ]
                    )
                if len(color_options) > 1:
                    raise ValidationError("1 color option needed for gradient.")
            if "displayvaluecoloroption_set-0-color_level" in self.data and float(
                self.data["gradient_higher_level"]
            ) <= float(self.data.get("displayvaluecoloroption_set-0-color_level")):
                raise ValidationError(
                    "gradient higher level must be strictly higher than the color option level."
                )
            if not len(color_options) == 1:
                raise ValidationError("1 color option needed for gradient.")
            if self.data.get("displayvaluecoloroption_set-0-color") == "":
                raise ValidationError(
                    "Color for Display value color options cannot be null for gradient."
                )
            if self.data["color"] == "":
                raise ValidationError("Color cannot be null for gradient.")

    class Meta:
        widgets = {
            "gradient": forms.CheckboxInput(
                attrs={
                    "--hideshow-fields": "gradient_higher_level,",
                    # gradient_higher_level visible if checkbox checked
                    "--show-on-checked": "gradient_higher_level,",
                }
            ),
        }

    class Media:
        js = ("pyscada/js/admin/hideshow.js",)


class DisplayValueColorOptionAdminFrom(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DisplayValueColorOptionAdminFrom, self).__init__(*args, **kwargs)
        wtf = Color.objects.all()
        w = self.fields["color"].widget
        color_choices = [(None, None)]
        for choice in wtf:
            color_choices.append((choice.id, choice.color_code()))
        w.choices = color_choices

        def create_option_color(
            self, name, value, label, selected, index, subindex=None, attrs=None
        ):
            if label is None:
                return self._create_option(
                    name, value, label, selected, index, subindex, attrs=None
                )
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
                attrs={"style": "background: %s; color: #%s" % (label, font_color)},
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


class DisplayValueColorOptionInline(admin.TabularInline):
    model = DisplayValueColorOption
    form = DisplayValueColorOptionAdminFrom
    extra = 0


class TransformDataAdmin(admin.ModelAdmin):
    # only allow viewing and deleting
    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class DisplayValueOptionTemplateAdmin(admin.ModelAdmin):
    # only allow viewing and deleting
    def has_module_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


class DisplayValueOptionAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "template",
                    "timestamp_conversion",
                    "transform_data",
                    "from_timestamp_offset",
                ),
            },
        ),
        (
            "Color",
            {
                "fields": (
                    "color",
                    "color_only",
                    "gradient",
                    "gradient_higher_level",
                ),
            },
        ),
    )
    form = DisplayValueOptionAdminFrom
    save_as = True
    save_as_continue = True
    inlines = [DisplayValueColorOptionInline]
    # Add inlines for any model with OneToOne relation with Device
    related_models = [
        field
        for field in DisplayValueOption._meta.get_fields()
        if issubclass(type(field), OneToOneRel)
    ]
    for m in related_models:
        model_dict = dict(model=m.related_model)
        if hasattr(m.related_model, "FormSet"):
            model_dict["formset"] = m.related_model.FormSet
        cl = type(m.name, (admin.StackedInline,), model_dict)  # classes=['collapse']
        inlines.append(cl)

    def has_module_permission(self, request):
        return False

    class Media:
        js = (
            # To be sure the jquery files are loaded before our js file
            "admin/js/vendor/jquery/jquery.min.js",
            "admin/js/jquery.init.js",
            # only the inline corresponding to the transform data selected
            "pyscada/js/admin/display_inline_transform_data_display_value_option.js",
        )


class ControlElementOptionAdmin(admin.ModelAdmin):
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


class ControlItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "position",
        "label",
        "type",
        "variable",
        "variable_property",
        "display_value_options",
        "control_element_options",
    )
    list_filter = (
        "controlpanel",
        FormListFilter,
        "type",
    )
    list_editable = (
        "position",
        "label",
        "type",
        "variable",
        "variable_property",
        "display_value_options",
        "control_element_options",
    )
    raw_id_fields = ("variable",)
    save_as = True
    save_as_continue = True


class SlidingPanelMenuForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SlidingPanelMenuForm, self).__init__(*args, **kwargs)
        wtf = ControlItem.objects.all()
        w = self.fields["items"].widget
        choices = []
        for choice in wtf:
            choices.append(
                (
                    choice.id,
                    choice.label
                    + " ("
                    + choice.variable.name
                    + ", "
                    + choice.get_type_display()
                    + ")",
                )
            )
        w.choices = choices


class SlidingPanelMenuAdmin(admin.ModelAdmin):
    # search_fields = ['name',]
    # filter_horizontal = ('items',)
    # form = SlidingPanelMenuForm
    list_display = ("id", "title", "position", "visible")
    save_as = True
    save_as_continue = True


class WidgetAdmin(admin.ModelAdmin):
    list_display_links = ("id",)
    list_display = (
        "id",
        "title",
        "page",
        "row",
        "col",
        "size",
        "content",
        "visible",
        "extra_css_class",
    )
    list_editable = (
        "title",
        "page",
        "row",
        "col",
        "size",
        "content",
        "visible",
        "extra_css_class",
    )
    list_filter = ("page",)
    save_as = True
    save_as_continue = True


class GroupDisplayPermissionForm(forms.ModelForm):
    def clean(self):
        super().clean()
        hmi_group = self.cleaned_data.get("hmi_group", None)
        id = self.instance.pk
        unauthenticated_users = self.instance.unauthenticated_users
        if len(
            GroupDisplayPermission.objects.filter(hmi_group=hmi_group, unauthenticated_users=unauthenticated_users).exclude(id=id)
        ):
            raise ValidationError("This group display permission already exist.")


class GroupDisplayPermissionAdmin(admin.ModelAdmin):
    filter_horizontal = ()
    save_as = True
    save_as_continue = True
    form = GroupDisplayPermissionForm
    readonly_fields = ["unauthenticated_users"]

    def get_fields(self, request, obj=None):
        # show unauthenticated_users field only for the GroupDisplayPermission used for unauthenticated users and hide hmi_group
        # show hmi_group field in other cases and hide the unauthenticated_users field
        if obj is not None and obj.unauthenticated_users:
            return ("unauthenticated_users",)
        return ('hmi_group',)

    def get_inlines(self, request, obj=None):
        # Add inlines for any model with OneToOne relation with Device
        items = [
            field
            for field in GroupDisplayPermission._meta.get_fields()
            if issubclass(type(field), OneToOneRel)
        ]
        inlines = []
        for d in items:
            filter_horizontal_inline = ()
            for field in d.related_model._meta.local_many_to_many:
                filter_horizontal_inline += (field.name,)
            # Collapse inline only if empty
            if hasattr(obj, d.name):
                collapse = None
            else:
                collapse = ["collapse"]
            device_dict = dict(
                model=d.related_model,
                filter_horizontal=filter_horizontal_inline,
                classes=collapse,
            )
            cl = type(d.name, (admin.TabularInline,), device_dict)
            inlines.append(cl)
        return inlines

    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.hmi_group is None:
            return False
        return super().has_delete_permission(request, obj)


class ControlPanelAdmin(admin.ModelAdmin):
    filter_horizontal = (
        "items",
        "forms",
    )
    save_as = True
    save_as_continue = True


class ViewAdmin(admin.ModelAdmin):
    filter_horizontal = ("pages", "sliding_panel_menus")
    save_as = True
    save_as_continue = True


class CustomHTMLPanelAdmin(admin.ModelAdmin):
    filter_horizontal = ("variables", "variable_properties")
    save_as = True
    save_as_continue = True


class PageAdmin(admin.ModelAdmin):
    list_display_links = ("id",)
    list_display = (
        "id",
        "title",
        "link_title",
        "position",
    )
    list_editable = (
        "title",
        "link_title",
        "position",
    )
    list_filter = ("view__title",)
    save_as = True
    save_as_continue = True


class ProcessFlowDiagramItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "control_item",
        "top",
        "left",
        "width",
        "height",
        "visible",
        "font_size",
    )
    list_editable = (
        "control_item",
        "top",
        "left",
        "width",
        "height",
        "visible",
        "font_size",
    )
    # raw_id_fields = ('variable',)
    save_as = True
    save_as_continue = True


class ProcessFlowDiagramAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "type",
        "background_image",
    )
    list_editable = (
        "title",
        "type",
        "background_image",
    )
    filter_horizontal = ("process_flow_diagram_items",)
    save_as = True
    save_as_continue = True


class ThemeForm(forms.ModelForm):
    def clean(self):
        super().clean()
        try:
            get_template(self.cleaned_data["base_filename"] + ".html").render()
        except TemplateDoesNotExist as e:
            raise ValidationError(f"Template {e} not found.")
        try:
            get_template(self.cleaned_data["view_filename"] + ".html").render(
                {"base_html": self.cleaned_data.get("base_filename", "base") + ".html"}
            )
        except TemplateDoesNotExist as e:
            raise ValidationError(f"Template {e} not found.")


class ThemeAdmin(admin.ModelAdmin):
    save_as = True
    save_as_continue = True
    form = ThemeForm

    def has_module_permission(self, request):
        return False


class CssClassAdmin(admin.ModelAdmin):
    save_as = True
    save_as_continue = True

    def has_module_permission(self, request):
        return False


admin_site.register(ControlItem, ControlItemAdmin)
admin_site.register(Chart, ChartAdmin)
admin_site.register(Pie, PieAdmin)
admin_site.register(Form, FormAdmin)
admin_site.register(SlidingPanelMenu, SlidingPanelMenuAdmin)
admin_site.register(Page, PageAdmin)
admin_site.register(GroupDisplayPermission, GroupDisplayPermissionAdmin)
admin_site.register(DisplayValueOption, DisplayValueOptionAdmin)
admin_site.register(ControlElementOption, ControlElementOptionAdmin)
admin_site.register(ControlPanel, ControlPanelAdmin)
admin_site.register(CustomHTMLPanel, CustomHTMLPanelAdmin)
admin_site.register(Widget, WidgetAdmin)
admin_site.register(View, ViewAdmin)
admin_site.register(ProcessFlowDiagram, ProcessFlowDiagramAdmin)
admin_site.register(ProcessFlowDiagramItem, ProcessFlowDiagramItemAdmin)
admin_site.register(Theme, ThemeAdmin)
admin_site.register(CssClass, CssClassAdmin)
admin_site.register(TransformData, TransformDataAdmin)
admin_site.register(DisplayValueOptionTemplate, DisplayValueOptionTemplateAdmin)
