# -*- coding: utf-8 -*-
from django.template import Context, loader
from pyscada.models import Clients
from pyscada.models import ClientConfig
from pyscada.models import RecordedTime
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataBoolean
from pyscada.models import Variables
from pyscada.models import InputConfig
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.utils import timezone
import json

def index(request):
	t = loader.get_template('content.html')	
	Inputs = InputConfig.objects.filter(active=1)
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
	varIdList = request.POST.getlist('varIds[]')
	var_id = int(varIdList[0])
	timestamp = float(request.POST['timestamp'])
	#for item in request.POST.getlist('value2[]'):
	#		out =  out + 'value2' + ':' + item
	
	
	# query data
	# query timestamp pk's 
	tValues = RecordedTime.objects.filter(timestamp__gt = timezone.datetime.fromtimestamp((timestamp/1000.0), tz=timezone.get_current_timezone())).order_by('-pk').values_list('id',flat=True)
	# query variable data
	qList = []
	for var_id in varIdList:
		dValues = RecordedData.objects.filter(time__in=list(tValues),variable_name_id=int(var_id))
		iValues = InputConfig.objects.get(id=int(var_id))
		dList = [] #create list
		
		for row in dValues: #populate list
			dList.append([time.mktime(row.time.timestamp.astimezone(timezone.get_current_timezone()).timetuple())*1000,row.value])
		qList.append({
			'label': iValues.variable_name +' = -000.00 '+iValues.unit.unit,
			'unit':iValues.unit.unit,
			'name':iValues.variable_name,
			'id':int(var_id),
			'data':dList,
			'yaxis': 1,
			'yaxislabel':''
			})
		
	data = json.dumps(qList,indent=2)
	#data = serializers.serialize('json', tValues,fields=('Value','VariableName','Unit','time'),indent=2,use_natural_keys=True)
	return HttpResponse(data, mimetype='application/json')


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
