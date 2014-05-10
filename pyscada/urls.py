# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.hmi.views.index'),
    url(r'^accounts/logout/$', 'pyscada.hmi.views.logout_view'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^json/cache_data/$', 'pyscada.hmi.views.get_cache_data'),
    url(r'^json/init_data/$', 'pyscada.hmi.views.data'),
    url(r'^json/log_data/$', 'pyscada.hmi.views.log_data'),
    url(r'^json/config/$', 'pyscada.hmi.views.config'),
    url(r'^form/log_entry/$', 'pyscada.hmi.views.form_log_entry'),
    url(r'^form/write_task/$', 'pyscada.hmi.views.form_write_task'),
]

urlpatterns = patterns('', *urlpatterns)