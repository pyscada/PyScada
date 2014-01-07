# -*- coding: utf-8 -*-
from pyscada.views import index, json_data, json_log
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.views.index'),
    url(r'^json/data/$', 'pyscada.views.data_value'),
    url(r'^json/log/$', 'pyscada.views.json_log'),
    url(r'^json/config/$', 'pyscada.views.config'),
]

urlpatterns = patterns('', *urlpatterns)