# -*- coding: utf-8 -*-
from pyscada.core.models import Log
from pyscada.core.models import ClientWriteTask
from pyscada.core import log
from pyscada.core.models import Client
from pyscada.core.models import Variable
from pyscada.core.models import RecordedDataCache
from pyscada.core.models import RecordedEvent
from pyscada.hmi.models import Chart
from pyscada.hmi.models import Page
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View


#from pyscada.export import timestamp_unix_to_matlab
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.core.management import call_command
from django.utils import timezone
from django.template import Context, loader,RequestContext
from django.template.response import TemplateResponse
from django.db import connection
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import requires_csrf_token
import time
import json

def index(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)

	view_list = View.objects.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).distinct()
	t = loader.get_template('view_overview.html')
	c = RequestContext(request,{
		'user': request.user,
		'view_list':view_list
	})
	return HttpResponse(t.render(c))

@requires_csrf_token
def view(request,link_title):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)

	page_template = loader.get_template('content_page.html')
	widget_row_template = loader.get_template('widget_row.html')

	try:
		view = View.objects.get(link_title=link_title)
	except:
		return HttpResponse(status=404)

	page_list = view.pages.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).distinct()

	sliding_panel_list = view.sliding_panel_menus.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).distinct()

	visible_widget_list = Widget.objects.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator,page__in=page_list.iterator).values_list('pk',flat=True)
	visible_custom_html_panel_list = CustomHTMLPanel.objects.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).values_list('pk',flat=True)
	visible_chart_list = Chart.objects.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).values_list('pk',flat=True)

	visible_control_element_list = GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator).values_list('control_items',flat=True)

	panel_list   = sliding_panel_list.filter(position__in=(1,2,))
	control_list = sliding_panel_list.filter(position=0)

	current_row = 0
	has_chart = False
	widgets = []
	widget_rows_html = ""
	pages_html = ""
	for page in view.pages.filter(groupdisplaypermission__hmi_group__in=request.user.groups.iterator).distinct():
		current_row = 0
		has_chart = False
		widgets = []
		widget_rows_html = ""
		for widget in page.widget_set.all():
			# check if row has changed
			if current_row <> widget.row:
				# render new widget row and reset all loop variables
				widget_rows_html += widget_row_template.render(RequestContext(request,{'row':current_row,'has_chart':has_chart,'widgets':widgets,'visible_control_element_list':visible_control_element_list}))
				current_row = widget.row
				has_chart = False
				widgets = []
			if not widget.pk in visible_widget_list:
				continue
			if not widget.visible:
				continue
			if widget.chart:
				if not widget.chart.visible():
					continue
				if not widget.chart.pk in visible_chart_list:
					continue
				has_chart = True
				widgets.append(widget)
			elif widget.control_panel:
				widgets.append(widget)
			elif widget.process_flow_diagram:
				widgets.append(widget)
			elif widget.custom_html_panel:
				if not widget.custom_html_panel.pk in visible_custom_html_panel_list:
					continue
				widgets.append(widget)
		widget_rows_html += widget_row_template.render(RequestContext(request,{'row':current_row,'has_chart':has_chart,'widgets':widgets,'visible_control_element_list':visible_control_element_list}))
		pages_html += page_template.render(RequestContext(request,{'page':page,'widget_rows_html':widget_rows_html}))

	c = {
		'page_list': page_list,
		'pages_html':pages_html,
		'panel_list': panel_list,
		'control_list':control_list,
		'user': request.user,
		'view_title':view.title
	}

	log.webnotice('open hmi',request.user)
	return TemplateResponse(request, 'view.html', c)

def log_data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	if request.POST.has_key('timestamp'):
		timestamp = float(request.POST['timestamp'])
	else:
		timestamp = time.time()-(300) # get log of last 5 minutes

	data = Log.objects.filter(level__gte=6,timestamp__gt=float(timestamp)).order_by('-timestamp')
	odata = []
	for item in data:
		odata.append({"timestamp":item.timestamp,"level":item.level,"message":item.message,"username":item.user.username if item.user else "None"})
	jdata = json.dumps(odata,indent=2)

	return HttpResponse(jdata, content_type='application/json')

def form_log_entry(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	if request.POST.has_key('message') and request.POST.has_key('level'):
		log.add(request.POST['message'],request.POST['level'],request.user)
		return HttpResponse(status=200)
	else:
		return HttpResponse(status=404)

def	form_write_task(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	if request.POST.has_key('var_id') and request.POST.has_key('value'):
		cwt = ClientWriteTask(variable_id = request.POST['var_id'],value=request.POST['value'],start=time.time(),user=request.user)
		cwt.save()
		return HttpResponse(status=200)
	else:
		return HttpResponse(status=404)

def get_cache_data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)

	timestamp = time.time()-120*60
	if request.POST.has_key('timestamp'):
		timestamp = max(float(request.POST['timestamp'])/1000.0,timestamp) # prevent from loading more then 120 Minutes of Data
	if request.POST.has_key('init'):
		init = request.POST.has_key('init')
	else:
		init = False

	if request.POST.has_key('variables[]'):
		variables = request.POST.getlist('variables[]')
	else:
		return HttpResponse('{\n}', content_type='application/json')

	data = {}
	if RecordedDataCache.objects.last():
		data["timestamp"] = RecordedDataCache.objects.last().last_update_ms()
		data["server_time"] = time.time()*1000
	else:
		return HttpResponse('{\n}', content_type='application/json')

	raw_data = list(RecordedDataCache.objects.filter(variable_id__in=variables,last_update__gt=timestamp).values_list('variable__name','float_value','int_value','last_update','last_change'))

	for var in raw_data:
		if not data.has_key(var[0]):
			data[var[0]] = [];
		if var[4] != var[3] and init:  # if value is constant add a phantom datapoint
			if var[1]!=None:
				data[var[0]].append([var[4]*1000,var[1]])
			else:
				data[var[0]].append([var[4]*1000,var[2]])
		if var[1]!=None:
			data[var[0]].append([var[3]*1000,var[1]])
		else:
			data[var[0]].append([var[3]*1000,var[2]])



	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, content_type='application/json')

def logout_view(request):
	log.webnotice('logout',request.user)
	logout(request)
	# Redirect to a success page.
	return redirect('/accounts/login/?next=/')

def user_profile_change(request):
	return redirect('/accounts/login/?next=/')

def dataaquisition_daemon_start(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)

	call_command('PyScadaDaemon start')
	return HttpResponse(status=200)

def dataaquisition_daemon_stop(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)

	call_command('PyScadaDaemon stop')
	return HttpResponse(status=200)
