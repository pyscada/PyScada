# -*- coding: utf-8 -*-
from pyscada.models import Client
from pyscada.models import ClientConfig
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import InputConfig
from pyscada.models import RecordedTime
from pyscada import log
#from pyscada.export import timestamp_unix_to_matlab
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.utils import timezone
from django.template import Context, loader

import json

def index(request):
	t = loader.get_template('content.html')	
	#Inputs = InputConfig.objects.filter(active=1)
	Inputs = {}
	c = Context({
		'inputValues' : Inputs,
		'title': 'DataView'
	})
	return HttpResponse(t.render(c))
	#return render(request, 'content.html', c, content_type="application/xhtml+xml")
	
def config(request):
	
	config = {}
	config["DataFile"] 		= "json/data/"
	config["RefreshRate"] 	= 5000
	config["config"] = [
				{
				"xaxis":
					{
						"ticks":6
					},
				"axes":
					[
						{
						"yaxis":
							{
								"min":0,
								"max":120
							}
						}
					],
				"placeholder":"#chart-0",
				"legendplaceholder":"#chart-0-legend",
				"variables":
					{
						"t_2Di_1":{"yaxis":1,"color":0,"unit":"°C"},
						"t_2Do_1":{"yaxis":1,"color":1,"unit":"°C"},
						"t_2Di_1_r":{"yaxis":1,"color":2,"unit":"°C"},
						"t_2Do_1_r":{"yaxis":1,"color":3,"unit":"°C"},
						"t_2Di_1_set":{"yaxis":1,"color":4,"unit":"°C"},
						"t_1Ai_1":{"yaxis":1,"color":5,"unit":"°C"},
						"t_1Ai_1_set":{"yaxis":1,"color":6,"unit":"°C"},
						"t_1Ci_1":{"yaxis":1,"color":7,"unit":"°C"},
						"t_1Co_1":{"yaxis":1,"color":8,"unit":"°C"},
						"t_1Co_1_set":{"yaxis":1,"color":9,"unit":"°C"},
						"t_0Ei_1":{"yaxis":1,"color":10,"unit":"°C"},
						"t_0Ei_1_r":{"yaxis":1,"color":11,"unit":"°C"},
						"t_0Eo_1":{"yaxis":1,"color":12,"unit":"°C"},
						"t_0Eo_1_r":{"yaxis":1,"color":13,"unit":"°C"},
						"t_0Ei_1_set":{"yaxis":1,"color":14,"unit":"°C"},
						"t_0Eo_1_set":{"yaxis":1,"color":15,"unit":"°C"},
						"T_ERa_1":{"yaxis":1,"color":16,"unit":"°C"},
						"T_ERd_1":{"yaxis":1,"color":17,"unit":"°C"},
						"T_HWi_1":{"yaxis":1,"color":18,"unit":"°C"},
						"T_ASa_1":{"yaxis":1,"color":19,"unit":"°C"},
						"T_CRs_1":{"yaxis":1,"color":20,"unit":"°C"},
						"T_HWo_1":{"yaxis":1,"color":21,"unit":"°C"},
						"T_DSo_1":{"yaxis":1,"color":22,"unit":"°C"},
						"T_HSo_1":{"yaxis":1,"color":23,"unit":"°C"},
						"T_DWa_1":{"yaxis":1,"color":24,"unit":"°C"}
					}
				}
			]
	
	
	jdata = json.dumps(config,indent=2)
	return HttpResponse(jdata, mimetype='application/json')
	
	
def data(request):
	# read POST data
	if request.POST.has_key('timestamp'):
		timestamp = float(request.POST['timestamp'])
		# query timestamp pk's
		last_time_id 	= RecordedTime.objects.last().pk
		first_time_id 	= RecordedTime.objects.filter(timestamp__gte=timestamp).first()
		if first_time_id:
			first_time_id = first_time_id.pk
		else:
			return HttpResponse('{\n}', mimetype='application/json')
	else:
		# fetch only the last element
		last_time_id 	= RecordedTime.objects.last().pk
		first_time_id 	= last_time_id
	data = {}
	for val in Variable.objects.all():
		variable_class = InputConfig.objects.get_value_by_key('class',variable_id=val.pk).replace(' ','')
		if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
			r_values = RecordedDataFloat.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time__timestamp','value')
		elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
			r_values = RecordedDataInt.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time__timestamp','value')
		elif variable_class.upper() in ['BOOL']:
			r_values = RecordedDataBoolean.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time__timestamp','value')
		
		if r_values.count() > 0:
			data[val.variable_name] = list(r_values)
	
	
	
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, mimetype='application/json')
	
	
def data_value(request):
	# read POST data
	
	data = {}
	data["timestamp"] = RecordedTime.objects.last().timestamp
	for val in Variable.objects.all():
		variable_class = InputConfig.objects.get_value_by_key('class',variable_id=val.pk).replace(' ','')
		if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
			r_values = RecordedDataFloat.objects.filter(variable=val).last()
		elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
			r_values = RecordedDataInt.objects.filter(variable=val).last()
		elif variable_class.upper() in ['BOOL']:
			r_values = RecordedDataBoolean.objects.filter(variable=val).last()
		
		if r_values:
			data[val.variable_name] = r_values.value
	
	
	
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, mimetype='application/json')


def json_data(request):
	# read POST data
	if request.POST.has_key('timestamp'):
		timestamp = float(request.POST['timestamp'])
		# query timestamp pk's
		last_time_id 	= RecordedTime.objects.last().pk
		first_time_id 	= RecordedTime.objects.filter(timestamp__gte=timestamp).first()
		if first_time_id:
			first_time_id = first_time_id.pk
		else:
			return HttpResponse('{\n}', mimetype='application/json')
	else:
		# fetch only the last element
		last_time_id 	= RecordedTime.objects.last().pk
		first_time_id 	= last_time_id
	
	# query data
	# query variable data
	rdo = RecordedTime.objects.filter(id__lte=last_time_id, id__gte=first_time_id)
	
	timevalues 	= rdo.values_list('timestamp',flat=True)
	time_ids 	= rdo.values_list('id',flat=True)
	#time_ids 	= list(time_ids)
	#log.info('')
	data = {}
	data['timestamps'] = timevalues
	vo = Variable.objects.all()
	for val in vo:
		variable_class = InputConfig.objects.get_value_by_key('class',variable_id=val.pk).replace(' ','')
		if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
			r_time_ids = RecordedDataFloat.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True)
			r_values = RecordedDataFloat.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True)
		elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
			r_time_ids = RecordedDataInt.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True)
			r_values = RecordedDataInt.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True)
		elif variable_class.upper() in ['BOOL']:
			r_time_ids = RecordedDataBoolean.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True)
			r_values = RecordedDataBoolean.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True)
		
		tmp = [0]*len(time_ids)
		t_idx = 0
		v_idx = 0
		nb_v_idx = len(r_time_ids)-1
		for id in time_ids:
			if nb_v_idx < v_idx: 
				if t_idx > 0:
					tmp[t_idx] = tmp[t_idx-1]
			else:
				if r_time_ids[v_idx]==id:
					tmp[t_idx] = r_values[v_idx]
					laid = id
					v_idx += 1
				elif t_idx > 0:
					tmp[t_idx] = tmp[t_idx-1]

				if nb_v_idx > v_idx:
					while r_time_ids[v_idx]<=id and v_idx <= nb_v_idx:
						log.debug(("double id %d in variable %d")%(id,val.pk))
						v_idx += 1
			t_idx += 1
		data[val.variable_name] = tmp
	
		
	jdata = json.dumps(data,indent=2)
	return HttpResponse(jdata, mimetype='application/json')


def json_log(request):

	
	qList =	{
			'label': iValues.variable_name +' = -000.00 '+iValues.unit.unit,
			'unit':iValues.unit.unit,
			'name':iValues.variable_name,
			'id':int(var_id),
			'data':dList,
			'yaxis': 1,
			'yaxislabel':''
			}
	data = json.dumps(qList,indent=2)
	return HttpResponse(data, mimetype='application/json')
