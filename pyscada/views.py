# -*- coding: utf-8 -*-
from pyscada.models import Clients
from pyscada.models import ClientConfig
from pyscada.models import Variables
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
	return render(request, 'content.html', c, content_type="application/xhtml+xml")
	
def data(request):
	tValues = RecordedTime.objects.all()[0:30]
	values = tValues.values_list('id',flat=True)
	dValues = recordedData.objects.filter(time__in=list(values))
	t = loader.get_template('data_table_1.html')	
	c = Context({
		'title': 'test Title',
		'TimeValues': tValues,
		'DataValues': dValues,
	})
	return HttpResponse(t.render(c))



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
		# fetch only the last etement
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
	vo = Variables.objects.all()
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
