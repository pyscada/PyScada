# -*- coding: utf-8 -*-

from pyscada.models import RecordedData
from pyscada.phant.models import PhantDevice
from pyscada.utils import extract_numbers_from_str

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from time import time
import json


@csrf_exempt
def input(request, public_key=None, json_response=False):

    def do_response(success,message):
        if json_response:
            jdata = json.dumps({"success":success,"message":message},indent=2)
            return HttpResponse(jdata, content_type='application/json')
        else:
            return HttpResponse('%s %s'%('1' if success else '0',message),content_type='text/plain')
    
    if False:
        #read values and private key from jsonp
        return do_response(False,"not implemented")
    elif 'private_key' in request.POST:
        # stream is post
        private_key = request.POST.get('private_key')
        values = request.POST.dict()
    elif 'HTTP_PHANT_PRIVATE_KEY' in request.META:
        private_key = request.META['HTTP_PHANT_PRIVATE_KEY']
        values = request.POST.dict()
    elif 'private_key' in request.GET:
        # stream is get
        private_key = request.GET.get('private_key')
        values = request.GET.dict()
    else:
        return do_response(False,"not a valid request")
        
    try:
        device = PhantDevice.objects.get(public_key=public_key)
    except:
        return do_response(False,'public key not valid')

    # validate private key, validate values and write to RecordedData
    if not device.private_key == private_key:
        return do_response(False,'wrong private key')
    # prepare the values for writing
    # todo what to do with the cov value
    output = []
    for item in device.phant_device.variable_set.filter(name__in=values.keys()):
        timestamp = time()
        if type(values[item.name]) in [str,unicode]:
            # convert from string to value
            values[item.name] = extract_numbers_from_str(values[item.name])
        # get prev_value from DB
        item.query_prev_value()
        # 
        if item.update_value(values[item.name],timestamp):
            output.append(item.create_recorded_data_element())
    
    if  isinstance(output,list):
        RecordedData.objects.bulk_create(output)
    
    return do_response(True,'success')
