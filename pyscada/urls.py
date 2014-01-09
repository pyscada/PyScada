# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.views.index'),
    url(r'^json/data/$', 'pyscada.views.data'),
    url(r'^json/latest_data/$', 'pyscada.views.latest_data'),
    url(r'^json/config/$', 'pyscada.views.config'),
]

urlpatterns = patterns('', *urlpatterns)