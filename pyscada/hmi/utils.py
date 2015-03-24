# -*- coding: utf-8 -*-
from pyscada.core import log
from pyscada.hmi.models import Chart
from pyscada.hmi.models import Page
from pyscada.hmi.models import ControlItem
from pyscada.hmi.models import ControlPanel
from pyscada.hmi.models import Widget
from pyscada.hmi.models import SlidingPanelMenu
from pyscada.hmi.models import View
#from pyscada.hmi.models import GroupDisplayPermisions
#from pyscada.hmi.models import HMIVariable
from pyscada.core.models import Variable

import json
import codecs

def update_HMI(json_data):
    data = json.loads(json_data)
    # Chart
    if data.has_key('Chart'):
		for chart in data['Chart']:
			co,created  = Chart.objects.get_or_create(id=chart['id'],defaults={'title':chart['title'],'x_axis_label':chart['x_axis_label'],'x_axis_ticks':chart['x_axis_ticks'],'y_axis_label':chart['y_axis_label'],'y_axis_min':chart['y_axis_min'],'y_axis_max':chart['y_axis_max']})
			if created:
				log.info(("created Chart: %s") %(chart['title']))
			else:
				log.info(("updated Chart: %s") %(chart['title']))
				co.title = chart['title']
				co.x_axis_label = chart['x_axis_label']
				co.x_axis_ticks = chart['x_axis_ticks']
				co.y_axis_label = chart['y_axis_label']
				co.y_axis_min = chart['y_axis_min']
				co.y_axis_max = chart['y_axis_max']
				co.save()
				co.variables.clear()
			co.variables.add(*Variable.objects.filter(pk__in=chart['variables']))
			co.save()
        
    # Page
    if data.has_key('Page'):
		for page in data['Page']:
			po,created  = Page.objects.get_or_create(id = page['id'],defaults={'link_title':page['link_title'],'title':page['title'],'position':page['position']})
			if created:
				log.info(("created Page: %s") %(page['link_title']))
			else:
				log.info(("updated Page: %s") %(page['link_title']))
				po.title = page['title']
				po.link_title = page['link_title']
				po.position = page['position']
				po.save()
			po.save()
    

    # ControlItem
    if data.has_key('ControlItem'):
		for item in data['ControlItem']:
			cio,created  = ControlItem.objects.get_or_create(id = item['id'], defaults={'label':item['label'],'position':item['position'],'type':item['type'],'variable_id':item['variable']})
			if created:
				log.info(("created ControlItem: %s") %(item['id']))
			else:
				log.info(("updated ControlItem: %s") %(item['id']))
				cio.label=item['label']
				cio.position=item['position']
				cio.type=item['type']
				cio.variable_id=item['variable']
				cio.save()
			cio.save()
    
    # ControlPanel
    if data.has_key('ControlPanel'):
		for item in data['ControlPanel']:
			cpo,created  = ControlPanel.objects.get_or_create(id = item['id'], defaults={'title':item['title']})
			if created:
				log.info(("created ControlPanel: %s") %(item['id']))
			else:
				log.info(("updated ControlPanel: %s") %(item['id']))
				cpo.title = item['title']
				cpo.save()
				cpo.items.clear()
			cpo.items.add(*ControlItem.objects.filter(pk__in=item['items']))
			cpo.save()
     
    # Widget
    if data.has_key('Widget'):
		for widget in data['Widget']:
			if widget.has_key('chart'):
				wo,created  = Widget.objects.get_or_create(id = widget['id'], defaults={'title':widget['title'],'page_id':widget['page'],'col':widget['col'],'row':widget['row'],'size':widget['size'],'chart_id':widget['chart']})
			if widget.has_key('control_panel'):
				wo,created  = Widget.objects.get_or_create(id = widget['id'], defaults={'title':widget['title'],'page_id':widget['page'],'col':widget['col'],'row':widget['row'],'size':widget['size'],'control_panel_id':widget['control_panel']})

			if created:
				log.info(("created Widget: %s") %(widget['id']))
			else:
				log.info(("updated Widget: %s") %(widget['id']))
				wo.title = widget['title']
				wo.page_id = widget['page']
				wo.col = widget['col']
				wo.row = widget['row']
				wo.size = widget['size']
				if widget.has_key('chart'):
					wo.chart_id = widget['chart']
				if widget.has_key('control_panel'):
					wo.control_panel_id = widget['control_panel']
				wo.save()
			wo.save()
    
    
    # SlidingPanelMenu
    if data.has_key('SlidingPanelMenu'):
		for item in data['SlidingPanelMenu']:
			spo,created  = SlidingPanelMenu.objects.get_or_create(id = item['id'], defaults={'title':item['title'],'position':item['position'],'control_panel_id':item['control_panel']})
			if created:
				log.info(("created SlidingPanelMenu: %s") %(item['id']))
			else:
				log.info(("updated SlidingPanelMenu: %s") %(item['id']))
				spo.title = item['title']
				spo.position = item['position']
				spo.control_panel_id = item['control_panel']
				spo.save()
			spo.save()
        
    # View
    if data.has_key('View'):
		for item in data['View']:
			vo,created  = View.objects.get_or_create(id = item['id'], defaults={'title':item['title'],'description':item['description'],'link_title':item['link_title'],'position':item['position']})
			if created:
				log.info(("created View: %s") %(item['id']))
			else:
				log.info(("updated View: %s") %(item['id']))
				vo.title = item['title']
				vo.description = item['description']
				vo.link_title = item['link_title']
				vo.position = item['position']
				vo.save()
			if item.has_key('pages'):    
				vo.pages.add(*Page.objects.filter(pk__in=item['pages']))
			if item.has_key('sliding_panel_menus'):
				vo.sliding_panel_menus.add(*SlidingPanelMenu.objects.filter(pk__in=item['sliding_panel_menus']))	
			vo.save()
