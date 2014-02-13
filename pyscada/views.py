# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import ClientConfig
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import InputConfig
from pyscada.models import RecordedTime
from pyscada.models import WebClientChart
from pyscada.models import WebClientPage
from pyscada.models import WebClientControlItem
from pyscada.models import WebClientSlidingPanelMenu
from pyscada.models import Log
from pyscada.models import ClientWriteTask
from pyscada import log
#from pyscada.export import timestamp_unix_to_matlab
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.utils import timezone
from django.template import Context, loader,RequestContext
from django.db import connection
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.core import serializers
from django.views.decorators.csrf import requires_csrf_token

import time
import json


@requires_csrf_token
def index(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	
	t = loader.get_template('content.html')
	page_list = WebClientPage.objects.filter(users__username=request.user.username)
	page_content = []
	for page in	page_list:
		chart_list = []
		chart_skip = []
		for chart in page.webclientchart_set.filter(users__username=request.user.username).order_by("position"):
			if chart_skip.count(chart.pk)>0:
				continue
			chart_list.append(chart)
			if chart.row.count() > 0 and chart.size == 'sidebyside':
				chart_skip.append(chart.row.first().pk)
		page_content.append({"page":page,"charts":chart_list})
	
	panel_list = WebClientSlidingPanelMenu.objects.filter(users__username=request.user.username)
	
	c = RequestContext(request,{
		'page_content': page_content,
		'panel_list'	 : panel_list,
		'user'		 : request.user
	})
	log.webnotice('user %s: opend WebApp'%request.user.username)
	return HttpResponse(t.render(c))
	
def config(request):
	if not request.user.is_authenticated():
		return redirect('/accounts/login/?next=%s' % request.path)
	config = {}
	config["DataFile"] 		= "json/latest_data/"
	config["InitialDataFile"] = "json/data/"
	config["LogDataFile"] = "json/log_data/"
	config["RefreshRate"] 	= 5000
	config["config"] 		= []
	chart_count 				= 0
	for chart in WebClientChart.objects.all():
		vars = {}
		c_count = 0
		for var in chart.variables.all().order_by('variable_name'):
			vars[var.variable_name] = {"yaxis":1,"color":c_count,"unit":var.unit.description}
			c_count +=1

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
	
	active_variables = list(WebClientChart.objects.filter(users__username=request.user.username).values_list('variables__pk',flat=True))
	active_variables += list(WebClientControlItem.objects.filter(users__username=request.user.username).values_list('variable__pk',flat=True))
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
	
	active_variables = WebClientChart.objects.filter(users__username=request.user.username).values_list('variables__pk',flat=True)
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

