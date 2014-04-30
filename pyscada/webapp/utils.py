# -*- coding: utf-8 -*-
from pyscada import log
from pyscada.webapp.models import Chart
from pyscada.webapp.models import Page
from pyscada.webapp.models import ControlItem
from pyscada.webapp.models import ControlPanel
from pyscada.webapp.models import ChartSet
from pyscada.webapp.models import Widget
from pyscada.webapp.models import SlidingPanelMenu
#from pyscada.webapp.models import GroupDisplayPermisions
from pyscada.webapp.models import VariableDisplayPropery
from pyscada.models import Variable

import json
import codecs

def update_HMI(json_data):
    data = json.loads(json_data)
    # Chart
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
    for page in data['Page']:
        po,created  = Page.objects.get_or_create(id = page['id'],defaults={'link_title':page['link_title'],'title':page['title']})
        if created:
            log.info(("created Page: %s") %(page['link_title']))
        else:
            log.info(("updated Page: %s") %(page['link_title']))
            po.title = page['title']
            po.link_title = page['link_title']
            po.save()
        po.save()
    
    # ChartSet
    for chart_set in data['ChartSet']:
        if chart_set['chart_1'] < 1:
            chart_set['chart_1'] = None
        if chart_set['chart_2'] < 1:
            chart_set['chart_2'] = None
        cso,created  = ChartSet.objects.get_or_create(id = chart_set['id'], defaults={'distribution':chart_set['distribution'],'chart_1_id':chart_set['chart_1'],'chart_2_id':chart_set['chart_2']})
        if created:
            log.info(("created ChartSet: %s") %(chart_set['id']))
        else:
            log.info(("updated ChartSet: %s") %(chart_set['id']))
            cso.distribution = chart_set['distribution']
            cso.chart_1_id = chart_set['chart_1']
            cso.chart_2_id = chart_set['chart_2']
            cso.save()
        cso.save()
    
    # Widget
    for widget in data['Widget']:
        wo,created  = Widget.objects.get_or_create(id = widget['id'], defaults={'title':widget['title'],'page_id':widget['page'],'col':widget['col'],'row':widget['row'],'size':widget['size'],'chart_set_id':widget['chart_set']})
        if created:
            log.info(("created Widget: %s") %(widget['id']))
        else:
            log.info(("updated Widget: %s") %(widget['id']))
            wo.title = widget['title']
            wo.page_id = widget['page']
            wo.col = widget['col']
            wo.row = widget['row']
            wo.size = widget['size']
            wo.chart_set_id = widget['chart_set']
            wo.save()
        wo.save()
    
    # ControlItem
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
    for item in data['ControlPanel']:
        cpo,created  = ControlPanel.objects.get_or_create(id = item['id'], defaults={'title':item['title']})
        if created:
            log.info(("created ControlPanel: %s") %(chart_set['id']))
        else:
            log.info(("updated ControlPanel: %s") %(chart_set['id']))
            cpo.title = item['title']
            cpo.save()
            cpo.items.clear()
        cpo.items.add(*ControlItem.objects.filter(pk__in=item['items']))
        cpo.save()
    # SlidingPanelMenu
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
    # Group permissions