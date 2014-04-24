# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

urlpatterns = [
    # Public pages
    url(r'^$', 'pyscada.webapp.views.index'),
    url(r'^accounts/logout/$', 'pyscada.webapp.views.logout_view'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^json/data/$', 'pyscada.webapp.views.data'),
    url(r'^json/log_data/$', 'pyscada.webapp.views.log_data'),
    url(r'^json/latest_data/$', 'pyscada.webapp.views.get_cache_data'),
    url(r'^json/config/$', 'pyscada.webapp.views.config'),
    url(r'^form/log_entry/$', 'pyscada.webapp.views.form_log_entry'),
    url(r'^form/write_task/$', 'pyscada.webapp.views.form_write_task'),
]

urlpatterns = patterns('', *urlpatterns)