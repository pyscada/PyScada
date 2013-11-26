# -*- coding: utf-8 -*-
from scada.models import ControllerConfig
from scada.models import InputConfig
from scada.models import RecordedData
from scada.models import RecordedTime
import scipy.io as sio
import numpy as np
from codecs import open
from datetime import timedelta
from datetime import datetime

class DatabaseExport():
	""" 
	export measurements from the database to a file
	"""
	def __init__(self):
		self.Controllers = ControllerConfig.objects.all()
		self.variables = {}
		self.data = {}
	
	def get_variable_data(self,id):
		if not self.variables.has_key(id):
			self.variables[id] = InputConfig.objects.get(id = id)
	
	def gen_data_row(self,timestamp,RowData):
		row = '';
		#row += timestamp.strftime("%d-%b-%Y %H:%M:%S, ")
		row += '%1.10f, ' %self.datetime_to_matlab_datenum(timestamp)
		ColCount = len(self.variables.viewkeys())
		for variableKey in self.variables.viewkeys():
			if RowData.has_key(variableKey):
				row += '%1.6f'%RowData[variableKey]
			ColCount -= 1;
			if ColCount != 0:
				row += ', '
		row += '\n'
		return row
		
	def read_data(self):
		for timeStamp in recordedTime.objects.all():
			RowValues = {}
			for RecordedDataRow in RecordedData.objects.filter(time_id=timeStamp.id):
				self.get_variable_data(RecordedDataRow.VariableName_id)
				RowValues[recordedDataRow.VariableName_id] = RecordedDataRow.Value
			self.data[timeStamp.id] = RowValues
	
	def datetime_to_matlab_datenum(self,dt):
		ord = dt.toordinal()
		mdn = dt + timedelta(days = 366)
		frac = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
		return mdn.toordinal() + frac
   
	def export_to_csv(self,filename):
		CSVfile = open(filename, 'w+',encoding="utf-8")
		ColCount = len(self.variables.viewkeys())
		row1 = 'timestamp, '
		row2 = 'Matlab datenum, ';
		row3 = 'days since 0000 00:00:00, '
		for variableKey in self.variables.viewkeys():
			row1 += '%s' %(self.variables[variableKey].VariableName)
			row2 += '%s' %(self.variables[variableKey].Unit.Unit)
			row3 += '%s' %(self.variables[variableKey].Description.replace(',',';'))
			ColCount -= 1;
			if ColCount != 0:
				row1 += ', '
				row2 += ', '
				row3 += ', '
		row1 += '\n'
		row2 += '\n'
		row3 += '\n'
		CSVfile.write(row3)
		CSVfile.write(row2)
		CSVfile.write(row1)
		for timeStamp in RecordedTime.objects.all():
			CSVfile.write(self.gen_data_row(timeStamp.timestamp,self.Data[timeStamp.id]))
		CSVfile.close()
	
	def export_to_mat(self,filename):
		self.vecData = {}
		for timeStamp in RecordedTime.objects.all():
			if self.vecData.has_key('time'):
				self.vecData['time'] = np.append(self.vecData['time'],self.datetime_to_matlab_datenum(timeStamp.timestamp))
			else:
				self.vecData['time'] = self.datetime_to_matlab_datenum(timeStamp.timestamp)
			for variableKey in self.variables.viewkeys():
				if self.Data[timeStamp.id].has_key(variableKey):
					value = self.Data[timeStamp.id][variableKey]
				else:
					value = 0
					
				if self.vecData.has_key(self.variables[variableKey].VariableName):
					self.vecData[self.variables[variableKey].VariableName] = np.append(self.vecData[self.variables[variableKey].VariableName],value)
				else:
					self.vecData[self.variables[variableKey].VariableName] = value
					
						
		sio.savemat(filename, self.vecData)