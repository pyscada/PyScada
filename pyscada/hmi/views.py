# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

import pyscada.hmi.models
from pyscada.core import version as core_version
from pyscada.models import RecordedData, VariableProperty, Variable, Device
from pyscada.models import Log
from pyscada.models import DeviceWriteTask, DeviceReadTask
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import Form
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import Chart
from pyscada.hmi.models import View
from pyscada.hmi.models import ProcessFlowDiagram
from pyscada.utils import gen_hiddenConfigHtml, get_group_display_permission_list

from django.http import HttpResponse
from django.template.loader import get_template
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import requires_csrf_token
from django.conf import settings
from django.core.exceptions import PermissionDenied

import time
import json
import logging

logger = logging.getLogger(__name__)

UNAUTHENTICATED_REDIRECT = settings.UNAUTHENTICATED_REDIRECT \
    if hasattr(settings, 'UNAUTHENTICATED_REDIRECT') else '/accounts/login/'


def unauthenticated_redirect(func):
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated:
            return redirect('%s?next=%s' % (UNAUTHENTICATED_REDIRECT, args[0].path))
        return func(*args, **kwargs)

    return wrapper


@unauthenticated_redirect
def index(request):
    if GroupDisplayPermission.objects.count() == 0:
        view_list = View.objects.all()
    else:
        view_list = get_group_display_permission_list(View.objects, request.user.groups.all())

    c = {
        'user': request.user,
        'view_list': view_list,
        'version_string': core_version,
        'link_target': settings.LINK_TARGET if hasattr(settings, 'LINK_TARGET') else '_blank'
    }
    return TemplateResponse(request, 'view_overview.html', c)  # HttpResponse(t.render(c))


@unauthenticated_redirect
@requires_csrf_token
def view(request, link_title):
    base_template = 'base.html'
    view_template = 'view.html'
    page_template = get_template('content_page.html')
    widget_row_template = get_template('widget_row.html')
    STATIC_URL = str(settings.STATIC_URL) if hasattr(settings, 'STATIC_URL') else 'static'

    try:
        v = get_group_display_permission_list(View.objects, request.user.groups.all()).filter(link_title=link_title).\
            first()
        if v is None:
            raise View.DoesNotExist
        #v = View.objects.get(link_title=link_title)
    except View.DoesNotExist as e:
        logger.warning(f"{request.user} has no permission for view {link_title}")
        raise PermissionDenied("You don't have access to this view.")
    except View.MultipleObjectsReturned as e:
        logger.error(f"{e} for view link_title", exc_info=True)
        raise PermissionDenied(f"Multiples views with this link : {link_title}")
        #return HttpResponse(status=404)

    if v.theme is not None:
        base_template = str(v.theme.base_filename) + ".html"
        view_template = str(v.theme.view_filename) + ".html"

    if GroupDisplayPermission.objects.count() == 0:
        # no groups
        page_list = v.pages.all()
        sliding_panel_list = v.sliding_panel_menus.all()
        visible_widget_list = Widget.objects.filter(page__in=page_list.iterator()).values_list('pk', flat=True)
        visible_custom_html_panel_list = CustomHTMLPanel.objects.all().values_list('pk', flat=True)
        visible_chart_list = Chart.objects.all().values_list('pk', flat=True)
        visible_control_element_list = ControlItem.objects.all().values_list('pk', flat=True)
        visible_form_list = Form.objects.all().values_list('pk', flat=True)
        visible_process_flow_diagram_list = ProcessFlowDiagram.objects.all().values_list('pk', flat=True)
    else:
        page_list = get_group_display_permission_list(v.pages, request.user.groups.all())
        sliding_panel_list = get_group_display_permission_list(v.sliding_panel_menus, request.user.groups.all())
        visible_widget_list = get_group_display_permission_list(Widget.objects, request.user.groups.all()).filter(
            page__in=page_list.iterator()).values_list('pk', flat=True)
        visible_custom_html_panel_list = get_group_display_permission_list(
            CustomHTMLPanel.objects, request.user.groups.all()).values_list('pk', flat=True)
        visible_chart_list = get_group_display_permission_list(Chart.objects, request.user.groups.all()).\
            values_list('pk', flat=True)
        visible_control_element_list = get_group_display_permission_list(
            ControlItem.objects, request.user.groups.all()).values_list('pk', flat=True)
        visible_form_list = get_group_display_permission_list(Form.objects, request.user.groups.all()).\
            values_list('pk', flat=True)
        visible_process_flow_diagram_list = get_group_display_permission_list(
            ProcessFlowDiagram.objects, request.user.groups.all()).values_list('pk', flat=True)

    panel_list = sliding_panel_list.filter(position__in=(1, 2,))
    control_list = sliding_panel_list.filter(position=0)

    pages_html = ""
    object_config_list = dict()
    custom_fields_list = dict()
    javascript_files_list = list()
    css_files_list = list()
    show_daterangepicker = False
    has_flot_chart = False
    add_context = {}

    for page in page_list:
        # process content row by row
        current_row = 0
        widget_rows_html = ""
        main_content = list()
        sidebar_content = list()
        topbar = False

        show_daterangepicker_temp = False
        show_timeline_temp = False

        for widget in page.widget_set.all():
            # check if row has changed
            if current_row != widget.row:
                # render new widget row and reset all loop variables
                widget_rows_html += widget_row_template.render(
                    {'row': current_row, 'main_content': main_content, 'sidebar_content': sidebar_content,
                     'sidebar_visible': len(sidebar_content) > 0, 'topbar': topbar}, request)
                current_row = widget.row
                main_content = list()
                sidebar_content = list()
                topbar = False
            if widget.pk not in visible_widget_list:
                continue
            if not widget.visible:
                continue
            if widget.content is None:
                continue
            kwargs = {'visible_control_element_list': visible_control_element_list,
                      'visible_form_list': visible_form_list}
            widget_extra_css_class = widget.extra_css_class.css_class if widget.extra_css_class is not None else ""
            mc, sbc, opts = widget.content.create_panel_html(widget_pk=widget.pk, widget_extra_css_class=widget_extra_css_class, user=request.user, **kwargs)
            if mc is not None and mc != "":
                main_content.append(dict(html=mc, widget=widget, topbar=sbc))
            else:
                logger.info("main_content of widget : %s is %s !" % (widget, mc))
            if sbc is not None:
                sidebar_content.append(dict(html=sbc, widget=widget))
            if type(opts) == dict and 'topbar' in opts and opts['topbar'] == True:
                topbar = True
            if type(opts) == dict and 'show_daterangepicker' in opts and opts['show_daterangepicker'] == True:
                show_daterangepicker = True
                show_daterangepicker_temp = True
            if type(opts) == dict and 'show_timeline' in opts and opts['show_timeline'] == True:
                show_timeline_temp = True
            if type(opts) == dict and 'flot' in opts and opts['flot']:
                has_flot_chart = True
            if type(opts) == dict and 'base_template' in opts:
                base_template = opts['base_template']
            if type(opts) == dict and 'view_template' in opts:
                view_template = opts['view_template']
            if type(opts) == dict and 'add_context' in opts:
                add_context.update(opts['add_context'])
            if type(opts) == dict and 'javascript_files_list' in opts:
                for file_src in opts['javascript_files_list']:
                    if {'src': file_src} not in javascript_files_list:
                        javascript_files_list.append({'src': file_src})
            if type(opts) == dict and 'css_files_list' in opts:
                for file_src in opts['css_files_list']:
                    if {'src': file_src} not in css_files_list:
                        css_files_list.append({'src': file_src})
            if type(opts) == dict and 'object_config_list' in opts and type(opts['object_config_list'] == list):
                for obj in opts['object_config_list']:
                    model_name = str(obj._meta.model_name).lower()
                    if model_name not in object_config_list:
                        object_config_list[model_name] = list()
                    if obj not in object_config_list[model_name]:
                        object_config_list[model_name].append(obj)
            if type(opts) == dict and 'custom_fields_list' in opts and type(opts['custom_fields_list'] == list):
                for model in opts['custom_fields_list']:
                    custom_fields_list[str(model).lower()] = opts['custom_fields_list'][model]

        widget_rows_html += widget_row_template.render(
            {'row': current_row, 'main_content': main_content, 'sidebar_content': sidebar_content,
             'sidebar_visible': len(sidebar_content) > 0, 'topbar': topbar}, request)

        pages_html += page_template.render({'page': page,
                                            'widget_rows_html': widget_rows_html,
                                            'show_daterangepicker': show_daterangepicker_temp,
                                            'show_timeline': show_timeline_temp,
                                            }, request)

    # Generate javascript files list
    if has_flot_chart:
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/jquery/jquery.tablesorter.min.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/lib/jquery.mousewheel.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.canvaswrapper.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.colorhelpers.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.saturated.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.browser.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.drawSeries.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.errorbars.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.uiConstants.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.logaxis.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.symbol.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.flatdata.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.navigate.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.fillbetween.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.stack.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.touchNavigate.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.hover.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.touch.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.time.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.axislabels.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.selection.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.composeImages.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.legend.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.pie.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.crosshair.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/flot/source/jquery.flot.gauge.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/jquery.flot.axisvalues.js'})

    if show_daterangepicker:
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/daterangepicker/moment.min.js'})
        javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/daterangepicker/daterangepicker.min.js'})

    javascript_files_list.append({'src': STATIC_URL + 'pyscada/js/pyscada/pyscada_v0-7-0rc14.js'})

    # Generate css files list
    css_files_list.append({'src': STATIC_URL + 'pyscada/css/daterangepicker/daterangepicker.css'})

    # Adding SlidingPanelMenu to hidden config
    for s in sliding_panel_list:
        if s.control_panel is not None:
            for obj in s.control_panel._get_objects_for_html(obj=s):
                if obj._meta.model_name not in object_config_list:
                    object_config_list[obj._meta.model_name] = list()
                if obj not in object_config_list[obj._meta.model_name]:
                    object_config_list[obj._meta.model_name].append(obj)
    # Generate html object hidden config
    pages_html += '<div class="hidden globalConfig2">'
    for model, val in sorted(object_config_list.items(), key = lambda ele: ele[0]):
        pages_html += '<div class="hidden ' + str(model) + 'Config2">'
        for obj in val:
            pages_html += gen_hiddenConfigHtml(obj, custom_fields_list.get(model, None))
        pages_html += '</div>'
    pages_html += '</div>'

    context = {
        'base_html': base_template,
        'include': [],
        'page_list': page_list,
        'pages_html': pages_html,
        'panel_list': panel_list,
        'control_list': control_list,
        'user': request.user,
        'visible_control_element_list': visible_control_element_list,
        'visible_form_list': visible_form_list,
        'view_title': v.title,
        'view_show_timeline': v.show_timeline,
        'version_string': core_version,
        'link_target': settings.LINK_TARGET if hasattr(settings, 'LINK_TARGET') else '_blank',
        'javascript_files_list': javascript_files_list,
        'css_files_list': css_files_list,
    }
    context.update(add_context)

    return TemplateResponse(request, view_template, context)


@unauthenticated_redirect
def log_data(request):
    if 'timestamp' in request.POST:
        timestamp = float(request.POST['timestamp'])
    else:
        timestamp = (time.time() - 300) * 1000  # get log of last 5 minutes

    data = Log.objects.filter(level__gte=6, id__gt=int(int(timestamp) * 2097152) + 2097151).order_by('-timestamp')
    odata = []
    for item in data:
        odata.append({"timestamp": item.timestamp * 1000, "level": item.level, "message": item.message,
                      "username": item.user.username if item.user else "None"})
    jdata = json.dumps(odata, indent=2)

    return HttpResponse(jdata, content_type='application/json')


@unauthenticated_redirect
def form_read_all_task(request):
    crts = []
    for device in Device.objects.all():
        crts.append(DeviceReadTask(device=device, start=time.time(), user=request.user))
    if len(crts) > 0:
        crts[0].create_and_notificate(crts)
    return HttpResponse(status=200)


@unauthenticated_redirect
def form_read_task(request):
    if 'key' in request.POST and 'type' in request.POST:
        key = int(request.POST['key'])
        item_type = request.POST['type']
        # check if float as DeviceWriteTask doesn't support string values
        if GroupDisplayPermission.objects.count() == 0:
            if item_type == 'variable':
                crt = DeviceReadTask(device=Variable.objects.get(pk=key).device, start=time.time(), user=request.user)
                crt.create_and_notificate(crt)
                return HttpResponse(status=200)
            elif item_type == 'variable_property':
                crt = DeviceReadTask(device=VariableProperty.objects.get(pk=key).variable.device, start=time.time(),
                                     user=request.user)
                crt.create_and_notificate(crt)
                return HttpResponse(status=200)
        else:
            if item_type == 'variable':
                if get_group_display_permission_list(ControlItem.objects, request.user.groups.all()).filter(
                        type=1, variable_id=key
                    ).exists():
                    crt = DeviceReadTask(device=Variable.objects.get(pk=key).device, start=time.time(),
                                         user=request.user)
                    crt.create_and_notificate(crt)
                    return HttpResponse(status=200)
                else:
                    logger.warning(f"User {request.user} has no right to add read task "
                                   f"for variable {Variable.objects.get(pk=key)}")
                    return HttpResponse(status=404)
            elif item_type == 'variable_property':
                if get_group_display_permission_list(ControlItem.objects, request.user.groups.all()).filter(
                        type=1, variable_property_id=key
                    ).exists():
                    crt = DeviceReadTask(device=VariableProperty.objects.get(pk=key).variable.device, start=time.time(),
                                         user=request.user)
                    crt.create_and_notificate(crt)
                    return HttpResponse(status=200)
                else:
                    logger.warning(f"User {request.user} has no right to add read task "
                                   f"for variable property {VariableProperty.objects.get(pk=key)}")
                    return HttpResponse(status=404)
        logger.warning(f"Wrong read task request, POST is : {request.POST}")
    return HttpResponse(status=404)


@unauthenticated_redirect
def form_write_task(request):
    if 'key' in request.POST and 'value' in request.POST:
        key = int(request.POST['key'])
        item_type = request.POST['item_type']
        value = request.POST['value']
        # check if float as DeviceWriteTask doesn't support string values
        try:
            float(value)
        except ValueError:
            logger.debug("form_write_task input is not a float")
            return HttpResponse(status=403)
        if GroupDisplayPermission.objects.count() == 0:
            if item_type == 'variable':
                cwt = DeviceWriteTask(variable_id=key, value=value, start=time.time(),
                                      user=request.user)
                cwt.create_and_notificate(cwt)
                return HttpResponse(status=200)
            elif item_type == 'variable_property':
                cwt = DeviceWriteTask(variable_property_id=key, value=value, start=time.time(),
                                      user=request.user)
                cwt.create_and_notificate(cwt)
                return HttpResponse(status=200)
        else:
            if item_type == 'variable':
                if get_group_display_permission_list(ControlItem.objects, request.user.groups.all()).filter(
                        type=0, variable_id=key
                    ).exists():
                    cwt = DeviceWriteTask(variable_id=key, value=value, start=time.time(),
                                          user=request.user)
                    cwt.create_and_notificate(cwt)
                    return HttpResponse(status=200)
                else:
                    logger.debug("Missing group display permission for write task (variable %s)" % key)
            elif item_type == 'variable_property':
                if get_group_display_permission_list(ControlItem.objects, request.user.groups.all()).filter(
                        type=0, variable_property_id=key
                    ).exists():
                    cwt = DeviceWriteTask(variable_property_id=key, value=value, start=time.time(),
                                          user=request.user)
                    cwt.create_and_notificate(cwt)
                    return HttpResponse(status=200)
                else:
                    logger.debug("Missing group display permission for write task (VP %s)" % key)
    else:
        logger.debug("key or value missing in request : %s" % request.POST)
    return HttpResponse(status=404)


@unauthenticated_redirect
def form_write_property2(request):
    if 'variable_property' in request.POST and 'value' in request.POST:
        value = request.POST['value']
        try:
            variable_property = int(request.POST['variable_property'])
            VariableProperty.objects.update_property(variable_property=variable_property, value=value)
        except ValueError:
            variable_property = str(request.POST['variable_property'])
            if VariableProperty.objects.get(name=variable_property).value_class.upper() in ['STRING']:
                VariableProperty.objects.update_property(variable_property=VariableProperty.objects.get(
                    name=variable_property), value=value)
            else:
                return HttpResponse(status=404)
        return HttpResponse(status=200)
    return HttpResponse(status=404)


def int_filter(someList):
    for v in someList:
        try:
            int(v)
            yield v  # Keep these
        except ValueError:
            continue  # Skip these


@unauthenticated_redirect
def get_cache_data(request):
    if 'init' in request.POST:
        init = bool(float(request.POST['init']))
    else:
        init = False
    active_variables = []
    if 'variables[]' in request.POST:
        active_variables = request.POST.getlist('variables[]')
        active_variables = list(int_filter(active_variables))
    """
    else:
        active_variables = list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'charts__variables', flat=True))
        active_variables += list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'control_items__variable', flat=True))
        active_variables += list(
            GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator()).values_list(
                'custom_html_panels__variables', flat=True))
        active_variables = list(set(active_variables))
    """

    active_variable_properties = []
    if 'variable_properties[]' in request.POST:
        active_variable_properties = request.POST.getlist('variable_properties[]')

    timestamp_from = time.time()
    if 'timestamp_from' in request.POST:
        timestamp_from = float(request.POST['timestamp_from']) / 1000.0
    if timestamp_from == 0:
        timestamp_from = time.time() - 60

    timestamp_to = time.time()
    if 'timestamp_to' in request.POST:
        timestamp_to = min(timestamp_to, float(request.POST['timestamp_to']) / 1000.0)
    if timestamp_to == 0:
        timestamp_to = time.time()

    #if timestamp_to - timestamp_from > 120 * 60 and not init:
    #    timestamp_from = timestamp_to - 120 * 60

    #if not init:
        #timestamp_to = min(timestamp_from + 30, timestamp_to)

    if len(active_variables) > 0:
        data = RecordedData.objects.db_data(
            variable_ids=active_variables,
            time_min=timestamp_from,
            time_max=timestamp_to,
            time_in_ms=True,
            query_first_value=init)
    else:
        data = None

    if data is None:
        data = {}

    # Add data for variable not logging to RecordedData model (as systemstat timestamps).
    for v_id in active_variables:
        if int(v_id) not in data:
            try:
                v = Variable.objects.get(id=v_id)
                v.query_prev_value(timestamp_from/1000)
                # add 5 seconds to let the request from the server to come
                if v.timestamp_old is not None and v.timestamp_old <= timestamp_to + 5 and v.prev_value is not None:
                    data[int(v_id)] = [[v.timestamp_old * 1000, v.prev_value]]
            except:
                #logger.warning(traceback.format_exc())
                pass

    data['variable_properties'] = {}
    data['variable_properties_last_modified'] = {}

    for item in VariableProperty.objects.filter(pk__in=active_variable_properties):
        data['variable_properties'][item.pk] = item.value()
        data['variable_properties_last_modified'][item.pk] = item.last_modified.timestamp() * 1000

    data["server_time"] = time.time() * 1000
    return HttpResponse(json.dumps(data), content_type='application/json')


def logout_view(request):
    logger.info('logout %s' % request.user)
    logout(request)
    # Redirect to a success page.
    return redirect('%s?next=%s' % (UNAUTHENTICATED_REDIRECT, '/'))


def user_profile_change(request):
    return redirect('%s?next=%s' % (UNAUTHENTICATED_REDIRECT, request.path))
