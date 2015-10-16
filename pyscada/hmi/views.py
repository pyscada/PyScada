# -*- coding: utf-8 -*-
from pyscada import version as core_version
from pyscada.models import Client
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import RecordedDataCache
from pyscada.models import RecordedTime
from pyscada.models import RecordedEvent
from pyscada.hmi.models import Chart
from pyscada.hmi.models import Page
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import CustomHTMLPanel
from pyscada.hmi.models import GroupDisplayPermission
from pyscada.hmi.models import Widget
from pyscada.hmi.models import View

from pyscada.models import Log
from pyscada.models import ClientWriteTask

from pyscada import log
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
			if not widget.visable:
				continue
			if widget.chart:
				if not widget.chart.visable():
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
		'visible_control_element_list':visible_control_element_list,
		'view_title':view.title,
		'version_string':core_version
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

		
	if request.POST.has_key('init'):
		init = bool(float(request.POST['init']))
	else:
		init = False

	if request.POST.has_key('variables[]'):
		active_variables = request.POST.getlist('variables[]')
	else:
		active_variables = list(GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator).values_list('charts__variables',flat=True))
		active_variables += list(GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator).values_list('control_items__variable',flat=True))
		active_variables += list(GroupDisplayPermission.objects.filter(hmi_group__in=request.user.groups.iterator).values_list('custom_html_panels__variables',flat=True))
		active_variables = list(set(active_variables))

	data = {}
	
		
	if init:
		timestamp = time.time()
		if request.POST.has_key('timestamp'):
			timestamp = max(float(request.POST['timestamp'])/1000.0,timestamp) # prevent from loading more then 120 Minutes of Data
		
		first_timestamp = time.time()-120*60
		if request.POST.has_key('first_timestamp'):
			timestamp = max(float(request.POST['first_timestamp'])/1000.0,timestamp) # prevent from loading more then 120 Minutes of Data
		
		if connection.vendor == 'sqlite':
			# on sqlite limit querys to less then 999 elements
			rto = list(reversed(RecordedTime.objects.filter(timestamp__gte=float(first_timestamp),timestamp__lt=float(timestamp)).order_by('-id')[:998].values_list('pk',flat=True)))
		else:
			rto = list(RecordedTime.objects.filter(timestamp__gte=float(first_timestamp),timestamp__lt=float(timestamp)).values_list('pk',flat=True))
	
		if rto:
			t_min_pk = rto[0]
			rto_ids     = rto
			t_min_ts = RecordedTime.objects.get(pk=t_min_pk).timestamp
		else:
			data["error"] = "no rto value"
			jdata = json.dumps(data,indent=2)
			return HttpResponse(jdata, content_type='application/json')

		for var in Variable.objects.filter(value_class__in = ('FLOAT32','SINGLE','FLOAT','FLOAT64','REAL',), pk__in = active_variables):
			var_id = var.pk
			rto = RecordedDataFloat.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
			if rto:
				data[var.name] = [(t_min_ts,rto.value)]
				data[var.name].extend(list(RecordedDataFloat.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value')))
			else:
				data[var.name] = list(RecordedDataFloat.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value'))
	
		for var in Variable.objects.filter(value_class__in = ('INT32','UINT32','INT16','INT','WORD','UINT','UINT16',),pk__in = active_variables):
			var_id = var.pk
			rto = RecordedDataInt.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
			if rto:
				data[var.name] = [(t_min_ts,rto.value)]
				data[var.name].extend(list(RecordedDataInt.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value')))
			else:
				data[var.name] = list(RecordedDataInt.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value'))
	
	
		for var in Variable.objects.filter(value_class__in = ('BOOL','BOOLEAN',), pk__in = active_variables):
			var_id = var.pk
			rto = RecordedDataBoolean.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
			if rto:
				data[var.name] = [(t_min_ts,rto.value)]
				data[var.name].extend(list(RecordedDataBoolean.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value')))
			else:
				data[var.name] = list(RecordedDataBoolean.objects.filter(variable_id=var_id,time_id__in=rto_ids).values_list('time__timestamp','value'))
				
		for key in data:
			for idx,item in enumerate(data[key]):
				data[key][idx] = (item[0]*1000,item[1])
		if RecordedDataCache.objects.last():
			data["timestamp"] = RecordedDataCache.objects.last().last_update_ms()
			data["server_time"] = time.time()*1000
		else:
			data["error"] = "no RecordedDataCache.objects.last() value"
			jdata = json.dumps(data,indent=2)
			return HttpResponse(jdata, content_type='application/json')
	else:
		
		data = {}
		if RecordedDataCache.objects.first():
			data["timestamp"] = RecordedDataCache.objects.last().time.timestamp_ms()
			data["server_time"] = time.time()*1000			
		else:
			data["error"] = "no RecordedDataCache.objects.last() value"
			jdata = json.dumps(data,indent=2)
			return HttpResponse(jdata, content_type='application/json')
		
		# read data from cache
		raw_data = list(RecordedDataCache.objects.filter(variable_id__in=active_variables).values_list('variable__name','value','time__timestamp'))
	
		for var in raw_data:
			data[var[0]] = [[var[2]*1000,var[1]]]
			
	data["init"] = init
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
