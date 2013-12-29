# -*- coding: utf-8 -*-
from pyscada.views import index, json_data, json_log
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.views.index'),
    url(r'^json/data/$', 'pyscada.views.json_data'),
    url(r'^json/log/$', 'pyscada.views.json_log'),
]

urlpatterns = patterns('', *urlpatterns)