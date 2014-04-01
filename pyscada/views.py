# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import ClientConfig
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import RecordedDataCache
from pyscada.models import InputConfig
from pyscada.models import RecordedTime
from pyscada.models import WebClientChart
from pyscada.models import WebClientPage
from pyscada.models import WebClientControlItem
from pyscada.models import WebClientSlidingPanelMenu
from pyscada.models import Log
from pyscada.models import ClientWriteTask
from pyscada.models import Group as PyGroup
from pyscada import log
#from pyscada.export import timestamp_unix_to_matlab
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.core.management import call_command
from django.utils import timezone
from django.template import Context, loader,RequestContext
from django.db import connection
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import requires_csrf_token

import time
import json


@requires_csrf_token
def index(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	
	t = loader.get_template('content.html')
	page_list = PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('pages',flat=True)
	page_content = []
	page_list = list(set(page_list))
	for page_id in	page_list:
		page = WebClientPage.objects.get(pk=page_id)
		chart_list = []
		chart_skip = []
		for chart in page.charts.filter(group__in=request.user.groups.iterator).order_by("position"):
			if chart_skip.count(chart.pk)>0:
				continue
			chart_list.append(chart)
			if chart.row.count() > 0 and (chart.size == 'sidebyside' or chart.size == 'sidebyside1'):
				chart_skip.append(chart.row.first().pk)
		page_content.append({"page":page,"charts":chart_list})
	
	sliding_panel_list = PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('sliding_panel_menu',flat=True)
	panel_list   = WebClientSlidingPanelMenu.objects.filter(pk__in=sliding_panel_list,position__in=(1,2,))
	control_list = WebClientSlidingPanelMenu.objects.filter(pk__in=sliding_panel_list,position=0)
	if control_list:
		control_list = control_list[0].items.all()
	c = RequestContext(request,{
		'page_content': page_content,
		'panel_list'	 : panel_list,
		'control_list':control_list,
		'user'		 : request.user
	})
	log.webnotice('user %s: opend WebApp'%request.user.username)
	return HttpResponse(t.render(c))
	
def config(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	config = {}
	config["DataFile"] 			= "json/latest_data/"
	config["InitialDataFile"] 	= "json/data/"
	config["LogDataFile"] 		= "json/log_data/"
	config["RefreshRate"] 		= 5000
	config["config"] 			= []
	chart_count 					= 0
	charts = PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('charts',flat=True)
	charts = list(set(charts))
	for chart_id in charts:
		vars = {}
		c_count = 0
		chart = WebClientChart.objects.get(pk=chart_id)
		for var in chart.variables.filter(active=1).order_by('variable_name'):
			if var.chart_line_color:
				if  var.chart_line_color.id > 1:
					color_code = var.chart_line_color.color_code()
				else:
					color_code = c_count
					c_count +=1
			else:
				color_code = c_count
				c_count +=1
			if (var.short_name and var.short_name != '-'):
				var_label = var.short_name
			else:
				var_label = var.variable_name
			vars[var.variable_name] = {"yaxis":1,"color":color_code,"unit":var.unit.description,"label":var_label}
			
		config["config"].append({"label":chart.label,"xaxis":{"ticks":chart.x_axis_ticks},"axes":[{"yaxis":{"min":chart.y_axis_min,"max":chart.y_axis_max,'label':chart.y_axis_label}}],"placeholder":"#chart-%d"% chart.pk,"legendplaceholder":"#chart-%d-legend" % chart.pk,"variables":vars}) 
		chart_count += 1		
	
	
	jdata = json.dumps(config,indent=2)
	return HttpResponse(jdata, content_type='application/json')

def log_data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	if request.POST.has_key('timestamp'):
		timestamp = float(request.POST['timestamp'])
	else:
		timestamp = time.time()-(60*60*24*14) # get log of last 14 days
		
	data = Log.objects.filter(level__gte=6,timestamp__gt=float(timestamp)).order_by('-timestamp')
	
	jdata = serializers.serialize("json", data,fields=('timestamp','level','message'))
	
	return HttpResponse(jdata, content_type='application/json')

def form_log_entry(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	if request.POST.has_key('message') and request.POST.has_key('level'):
		log.add(request.POST['message'],request.POST['level'])
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

def latest_data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	data = {}	
	data["timestamp"] = RecordedTime.objects.last().timestamp*1000
	t_pk = RecordedTime.objects.last().pk	
	
	active_variables = list(WebClientChart.objects.filter(groups__in=request.user.groups.iterator).values_list('variables__pk',flat=True))
	active_variables += list(WebClientControlItem.objects.filter(groups__in=request.user.groups.iterator).values_list('variable__pk',flat=True))
	cursor = connection.cursor()
	
	for val in Variable.objects.filter(value_class__in = ('FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'), pk__in = active_variables):
		var_id = val.pk
		r_values = cursor.execute("SELECT value FROM pyscada_recordeddatafloat where variable_id=%s AND time_id <= %s ORDER BY id DESC LIMIT 1;",[var_id,t_pk])
		if r_values >0:
			data[val.variable_name] = cursor.fetchone()[0]
	for val in Variable.objects.filter(value_class__in = ('INT32','UINT32','INT16','INT','WORD','UINT','UINT16'),pk__in = active_variables):
		var_id = val.pk
		r_values = cursor.execute("SELECT value FROM pyscada_recordeddataint where variable_id=%s AND time_id <= %s ORDER BY id DESC LIMIT 1;",[var_id,t_pk])
		if r_values >0:
			data[val.variable_name] = cursor.fetchone()[0]
	for val in Variable.objects.filter(value_class = 'BOOL', pk__in = active_variables):
		var_id = val.pk
		r_values = cursor.execute("SELECT value FROM pyscada_recordeddataboolean where variable_id=%s AND time_id <= %s ORDER BY id DESC LIMIT 1;",[var_id,t_pk])
		if r_values >0:
			data[val.variable_name] = cursor.fetchone()[0]
	
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, content_type='application/json')

def get_cache_data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	data = {}	
	data["timestamp"] = RecordedDataCache.objects.first().time.timestamp_ms()
	
	active_variables = list(PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('charts__variables',flat=True))
	active_variables += list(PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('control_items__variable',flat=True))
	
	active_variables = list(set(active_variables))
	raw_data = list(RecordedDataCache.objects.filter(variable_id__in=active_variables).values_list('variable__variable_name','value'))
	
	for var in raw_data:
		data[var[0]] = var[1]
	
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, content_type='application/json')

def data(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	# read POST data
	if request.POST.has_key('timestamp'):
		timestamp = float(request.POST['timestamp'])
	else:
		timestamp = time.time()-(15*60)
	
	# query timestamp pk's
	t_max_pk 		= RecordedTime.objects.last().pk
	rto 			= RecordedTime.objects.filter(timestamp__gte=float(timestamp))
	if rto.count()>0:
		t_min_ts 		= rto.first().timestamp
		t_min_pk 		= rto.first().pk
	else:
		return HttpResponse('{\n}', content_type='application/json')
	
	active_variables = PyGroup.objects.filter(group__in=request.user.groups.iterator).values_list('charts__variables',flat=True)
	active_variables = list(set(active_variables))
	
	data = {}
	
	for var in Variable.objects.filter(value_class__in = ('FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'), pk__in = active_variables):
		var_id = var.pk
		rto = RecordedDataFloat.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
		data[var.variable_name] = [(t_min_ts,rto.value)]
		data[var.variable_name].extend(list(RecordedDataFloat.objects.filter(variable_id=var_id,time_id__range=(t_min_pk,t_max_pk)).values_list('time__timestamp','value')))
		
	for var in Variable.objects.filter(value_class__in = ('INT32','UINT32','INT16','INT','WORD','UINT','UINT16'),pk__in = active_variables):
		var_id = var.pk
		rto = RecordedDataInt.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
		data[var.variable_name] = [(t_min_ts,rto.value)]
		data[var.variable_name].extend(list(RecordedDataInt.objects.filter(variable_id=var_id,time_id__range=(t_min_pk,t_max_pk)).values_list('time__timestamp','value')))
	

	for var in Variable.objects.filter(value_class = 'BOOL', pk__in = active_variables):
		var_id = var.pk
		rto = RecordedDataBoolean.objects.filter(variable_id=var_id,time_id__lt=t_min_pk).last()
		data[var.variable_name] = [(t_min_ts,rto.value)]
		data[var.variable_name].extend(list(RecordedDataBoolean.objects.filter(variable_id=var_id,time_id__range=(t_min_pk,t_max_pk)).values_list('time__timestamp','value')))
	for key in data:
		for idx,item in enumerate(data[key]):
			data[key][idx] = (item[0]*1000,item[1])
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, content_type='application/json')

def logout_view(request):
	logout(request)
	log.webnotice('user %s logged out'%request.user.username)
	# Redirect to a success page.
	return redirect('/accounts/login/')

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