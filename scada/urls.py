# -*- coding: utf-8 -*-
from scada.views import index, json_data, json_log
from django.conf.urls.defaults import url, patterns


urlpatterns = [
    # Public pages
    url(r'^$', 'scada.views.index'),
	url(r'^json/data/$', 'scada.views.json_data'),
	url(r'^json/log/$', 'scada.views.json_log'),
]

urlpatterns = patterns('', *urlpatterns)