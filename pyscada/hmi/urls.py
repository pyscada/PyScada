# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Public pages
    url(r'^$', views.index ,name="view-overview"),
    url(r'^accounts/logout/$', views.logout_view),
    url(r'^accounts/login/$', auth_views.login,{'template_name': 'login.html'},name='login_view'),
    url(r'^accounts/password_change/$', auth_views.password_change,{'template_name': 'password_change.html'},name='password_change'),
    url(r'^accounts/password_change_done/$', auth_views.password_change_done,{'template_name': 'password_change_done.html'},name='password_change_done'),
    url(r'^json/cache_data/$', views.get_cache_data),
    url(r'^json/log_data/$', views.log_data),
    url(r'^form/log_entry/$', views.form_log_entry),
    url(r'^form/write_task/$',views.form_write_task),
    url(r'^view/(?P<link_title>\w+)/$', views.view,name="main-view"),
]
