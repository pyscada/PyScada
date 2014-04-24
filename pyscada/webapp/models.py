# -*- coding: utf-8 -*-
from pyscada.models import Variable

from django.db import models 
from django.contrib.auth.models import Group

class Colors(models.Model):
	id 		= models.AutoField(primary_key=True)
	name 	= models.SlugField(max_length=80, verbose_name="variable name")
	R 		= models.PositiveSmallIntegerField(default=0)
	G 		= models.PositiveSmallIntegerField(default=0)
	B 		= models.PositiveSmallIntegerField(default=0)
	def __unicode__(self):
		return unicode('rgb('+str(self.R)+', '+str(self.G)+', '+str(self.B)+', '+')')
	def color_code(self):
		return unicode('#%02x%02x%02x' % (self.R, self.G, self.B))	

class VariableDisplayPropery(models.Model):
	webapp_variable		= models.OneToOneField(Variable)
	short_name			= models.CharField(default='',max_length=80, verbose_name="variable short name")
	chart_line_color 	= models.ForeignKey('Colors',default=0,null=True, on_delete=models.SET_NULL)
	chart_line_thickness_choices = ((3,'3Px'),)
	chart_line_thickness = models.PositiveSmallIntegerField(default=0,choices=chart_line_thickness_choices)



class ControlItem(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	type_choices 	= ((0,'label blue'),(1,'label light blue'),(2,'label ok'),(3,'label warning'),(4,'label alarm'),(5,'Control Element'),(6,'Display Value'),)
	type			= models.PositiveSmallIntegerField(default=0,choices=type_choices)
	variable    		= models.ForeignKey(Variable,null=True, on_delete=models.SET_NULL)
	def __unicode__(self):
		return unicode(self.label+" ("+self.variable.variable_name + ")")
	def web_id(self):
		return unicode(self.id.__str__() + "-" + self.label.replace(' ','_')+"-"+self.variable.variable_name.replace(' ','_'))

class Chart(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position			= models.PositiveSmallIntegerField(default=0)
	x_axis_label		= models.CharField(max_length=400, default='',blank=True)
	x_axis_ticks		= models.PositiveSmallIntegerField(default=6)
	y_axis_label		= models.CharField(max_length=400, default='',blank=True)
	y_axis_min		= models.FloatField(default=0)
	y_axis_max		= models.FloatField(default=100)
	size_choices 	= (('pagewidth','page width'),('sidebyside','side by side (1/2)'),('sidebyside1','side by side (2/3|1/3)'),)
	size			= models.CharField(max_length=20, default='pagewidth',choices=size_choices)
	variables		= models.ManyToManyField(Variable)
	row				= models.ManyToManyField("self",blank=True)
	def __unicode__(self):
		return unicode(self.label)
	
class SlidingPanelMenu(models.Model):
	id 				= models.AutoField(primary_key=True)
	label			= models.CharField(max_length=400, default='')
	position_choices = ((0,'Control Menu'),(1,'left'),(2,'right'))
	position			= models.PositiveSmallIntegerField(default=0,choices=position_choices)
	items	 	 	= models.ManyToManyField(ControlItem)
	def __unicode__(self):
		return unicode(self.label)
		
class Page(models.Model):
	id 				= models.AutoField(primary_key=True)
	title 			= models.CharField(max_length=400, default='')
	link_title		= models.SlugField(max_length=80, default='')
	charts 			= models.ManyToManyField(Chart,blank=True)
	def __unicode__(self):
		return unicode(self.link_title.replace(' ','_'))
		
class GroupDisplayPermisions(models.Model):
	webapp_group			= models.OneToOneField(Group)
	pages 				= models.ManyToManyField(Page,blank=True)
	sliding_panel_menu 	= models.ManyToManyField(SlidingPanelMenu,blank=True)
	charts 				= models.ManyToManyField(Chart,blank=True)
	control_items 		= models.ManyToManyField(ControlItem,blank=True)
	def __unicode__(self):
		return unicode(self.webapp_group.name)