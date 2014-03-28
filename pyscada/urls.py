# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.views.index'),
    url(r'^accounts/logout/$', 'pyscada.views.logout_view'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^json/data/$', 'pyscada.views.data'),
    url(r'^json/log_data/$', 'pyscada.views.log_data'),
    url(r'^json/latest_data/$', 'pyscada.views.get_cache_data'),
    url(r'^json/config/$', 'pyscada.views.config'),
    url(r'^form/log_entry/$', 'pyscada.views.form_log_entry'),
    url(r'^form/write_task/$', 'pyscada.views.form_write_task'),
]

urlpatterns = patterns('', *urlpatterns)