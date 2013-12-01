# -*- coding: utf-8 -*-
from django.db import models
#from django.db.models import fields
#from django.core import exceptions
#from django.conf import settings
#from django.db import connection as conn
#from django.utils.translation import ugettext as _
#from datetime import datetime
from django.utils import timezone
#from datetime import datetime
import time

#
# Custom field types in here.
#

class UnixTimestampField(models.FloatField):
    """UnixTimestampField: creates a timestamp field that is represented on the
    database as a double field rather than the usual DATETIME field.
    """
    def get_db_prep_value(self, value, connection, prepared=False):
        if self.auto_created:
            return  time.time()
        if value==None:
            return None
        return time.mktime(value.timetuple())

"""
    def __init__(self, null=False, blank=False, **kwargs):
        super(UnixTimestampField, self).__init__(**kwargs)
        # default for TIMESTAMP is NOT NULL unlike most fields, so we have to
        # cheat a little:
        # self.blank, self.isnull = blank, null
        # self.null = True # To prevent the framework from shoving in "not null".

    def db_type(self, connection):
        typ=['int']
        # See above!
        if self.null:
            typ += ['NULL']
        return ' '.join(typ)

    def get_db_prep_value(self, value, connection, prepared=False):
        if self.auto_created:
            return  int(time.time()*1000)
        if value==None:
            return None
        return int(1000*time.mktime(value.timetuple()))

    def to_python(self, value):
        if value is None:
            return value
        return float(value)/1000.0


class BigAutoField(fields.AutoField):

    def db_type(self):
        if settings.DATABASE_ENGINE == 'mysql':
            return "bigint AUTO_INCREMENT"
        elif settings.DATABASE_ENGINE == 'oracle':
            return "NUMBER(19)"
        elif settings.DATABASE_ENGINE[:8] == 'postgres':
            return "bigserial"
        else:
            raise NotImplemented

    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))

class BigForeignKey(fields.related.ForeignKey):

    def db_type(self):
        rel_field = self.rel.get_related_field()
        # next lines are the "bad tooth" in the original code:
        if (isinstance(rel_field, BigAutoField) or
                (not conn.features.related_fields_match_type and
                isinstance(rel_field, models.BigIntegerField))):
            # because it continues here in the django code:
            # return IntegerField().db_type()
            # thereby fixing any AutoField as IntegerField
            return models.BigIntegerField().db_type()
        return rel_field.db_type()

"""
#
# Manager
#

class RecordedDataValueManager(models.Manager):
	def by_time_id(self,time_id):
		data = super(RecordedDataValueManager, self).get_query_set().filter(time_id=time_id)
		output = {}
		for val in data:
			output[val.variable.variable_name] = val.value()
		return output

	def full_matrix_row_by_time_id(self,time_id):
		data = {}
		if super(RecordedDataValueManager, self).get_query_set().filter(time_id=time_id).count()==0:
			return data
		for val in Variables.objects.filter(active=1):
			if super(RecordedDataValueManager, self).get_query_set().filter(time_id__lt=time_id,variable=val).count() > 0:
				data[val.pk] = super(RecordedDataValueManager, self).get_query_set().filter(time_id__lt=time_id,variable=val).last().value()
			else:
				data[val.pk] = 0
		return data

	def variable_data_column(self,var_id,time_id_min,time_id_max):
		data = [];
		if not super(RecordedDataValueManager, self).get_query_set().filter(time_id__lt=time_id_max):
			return data
		if not super(RecordedDataValueManager, self).get_query_set().filter(time_id__gt=time_id_min):
			return data
		if not super(RecordedDataValueManager, self).get_query_set().filter(time_id__lt=time_id_min,variable_id=var_id):
			return data
		for t in RecordedTime.objects.filter(id__gt=time_id_min,id__lt=time_id_max):
			if super(RecordedDataValueManager, self).get_query_set().get(time_id=t.pk,variable_id=var_id):
				data.append(super(RecordedDataValueManager, self).get_query_set().filter(time_id=t.pk,variable_id=var_id).value())
			else:
				data.append(data[-1])
		return data

	def time_data_column(self,time_id_min,time_id_max):
		data = [];
		if RecordedTime.objects.filter(id__lt=time_id_max).count()==0:
			return data
		if RecordedTime.objects.filter(id__gt=time_id_min).count()==0:
			return data
		data = RecordedTime.objects.filter(id__gt=time_id_min,id__lt=time_id_max).values_list('timestamp',flat=True)
		return data

	def all(self):
		data = super(RecordedDataValueManager, self).get_query_set().all()
		output = {}
		for val in data:
			if not output.has_key(val.time.natural_key()):
				output[val.time.natural_key()] = {}
			output[val.time.natural_key()][val.variable.variable_name] = val.value()
		return output

	def later_then(self,timedelta):
		val_time = timezone.localtime(timezone.now())
		if timedelta.__class__.__name__ == 'timedelta':
			val_time = val_time - timedelta
		if timedelta.__class__.__name__ == 'datetime':
			val_time = timezone.localtime(timedelta)

		data = super(RecordedDataValueManager, self).get_query_set().filter(time__timestamp__gt = val_time)
		output = {}
		for val in data:
			if not output.has_key(val.time.natural_key()):
				output[val.time.natural_key()] = {}
			output[val.time.natural_key()][val.variable.variable_name] = val.value()
		return output


class KeyValueManager(models.Manager):
	def get_value_by_key(self,key,**kwargs):
		return super(KeyValueManager, self).get_query_set().get(key=key,**kwargs).value


class VariableConfigManager(models.Manager):
	def get_variable_input_config(self,client_id):
		variables = super(VariableConfigManager, self).get_query_set().filter(client_id=client_id,active=1)
		variable_config = {}
		for variable in variables:
			output = {};
			for entry in InputConfig.objects.filter(variable=variable.pk):
				if entry.key.find('.')==-1:
					output[entry.key] = entry.decoded_value()
				else:
					key_key = entry.key.split('.')[0]
					attr = entry.key.split('.')[1]
					if not output.has_key(key_key):
						output[key_key] = {}
					output[key_key][attr] = entry.decoded_value()
			output['variable_name']	= variable.variable_name;
			variable_config[variable.pk] = output
		return variable_config


class ClientConfigManager(models.Manager):
	def get_client_config(self,client_id):
		config = {}
		for entry in super(ClientConfigManager, self).get_query_set().filter(client_id=client_id):
			if entry.key.find('.')==-1:
				config[entry.key] = entry.decoded_value()
			else:
				key_key = entry.key.split('.')[0]
				attr = entry.key.split('.')[1]
				if not config.has_key(key_key):
					config[key_key] = {}
				config[key_key][attr] = entry.decoded_value()
		config['variable_input_config'] = Variables.objects.get_variable_input_config(client_id)
		return config
	def get_active_client_config(self):
		config = {}
		for entry in Clients.objects.all():
			if Variables.objects.filter(client_id=entry.pk,active=1).count()>0:
				config[entry.pk] = self.get_client_config(entry.pk)
		return config

#
# Model
#
class GlobalConfig(models.Model):
	id 			= models.AutoField(primary_key=True)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	description 	      = models.TextField(default='', verbose_name="Description")
	objects 		= KeyValueManager()

class Clients(models.Model):
	id 				= models.AutoField(primary_key=True)
	description 	= models.TextField(default='', verbose_name="Description")

	def __unicode__(self):
		return unicode(self.description)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)

class ClientConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	client			= models.ForeignKey('Clients',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	objects		= KeyValueManager()
	config			= ClientConfigManager()
	def __unicode__(self):
		return unicode(self.value)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)


class ScalingConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	description		= models.CharField(max_length=400, default='', verbose_name="Description")
	min_value		= models.FloatField(default=0, verbose_name="minimal Value")
	max_value		= models.FloatField(default="1", verbose_name="maximal Value")
	bit				= models.PositiveIntegerField(default=0, verbose_name="bit")
	def __unicode__(self):
		return unicode(self.description)


class UnitConfig(models.Model):
	id 				= models.AutoField(primary_key=True)
	unit			= models.CharField(max_length=80, verbose_name="Unit")
	description 	= models.TextField(default='', verbose_name="Description")
	def __unicode__(self):
		return unicode(self.unit)


class Variables(models.Model):
	id 				= models.AutoField(primary_key=True)
	variable_name 	= models.SlugField(max_length=80, verbose_name="variable name")
	description 	= models.TextField(default='', verbose_name="Description")
	client			= models.ForeignKey('Clients',null=True, on_delete=models.SET_NULL)
	active			= models.BooleanField()
	objects			= VariableConfigManager()
	def __unicode__(self):
		return unicode(self.variable_name)


class InputConfig(models.Model):
	id 			= models.AutoField(primary_key=True)
	variable	 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
	key 			= models.CharField(max_length=400, default='', verbose_name="key")
	value			= models.CharField(max_length=400, default='', verbose_name="value")
	objects 		= KeyValueManager()
	def __unicode__(self):
		return unicode(self.key)
	def decoded_value(self):
		if self.value.isdigit():
			return int(self.value)
		return unicode(self.value)

class RecordedTime(models.Model):
	#timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)
	id 			= models.AutoField(primary_key=True)
	timestamp 		= UnixTimestampField(auto_created=True)
	def __unicode__(self):
		return unicode(self.timestamp)


class RecordedDataFloat(models.Model):
    id            = models.AutoField(primary_key=True)
    value	      = models.FloatField()
    variable	 	= models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
    time		= models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
    objects 		= RecordedDataValueManager()
    def __unicode__(self):
        return unicode(self.value)

class RecordedDataInt(models.Model):
    id          = models.AutoField(primary_key=True)
    value       = models.IntegerField()
    variable    = models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
    time        = models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
    objects     = RecordedDataValueManager()
    def __unicode__(self):
        return unicode(self.value)

class RecordedDataBoolean(models.Model):
    id          = models.AutoField(primary_key=True)
    value       = models.NullBooleanField()
    variable    = models.ForeignKey('Variables',null=True, on_delete=models.SET_NULL)
    time        = models.ForeignKey('RecordedTime',null=True, on_delete=models.SET_NULL)
    objects     = RecordedDataValueManager()
    def __unicode__(self):
        return unicode(self.value)

class MessageIds(models.Model):
	id 	         = models.PositiveIntegerField(primary_key=True)
	level	         = models.PositiveIntegerField(default=0, verbose_name="error level")
	description 	  = models.TextField(default='', verbose_name="Description")


class Log(models.Model):
	id 				= models.AutoField(primary_key=True)
	message_id		= models.ForeignKey('MessageIds',null=True, on_delete=models.SET_NULL)
	timestamp 		= models.DateTimeField(auto_now=False, auto_now_add=True)
	message_short	= models.CharField(max_length=400, default='', verbose_name="short message")
	message 		= models.TextField(default='', verbose_name="message")


