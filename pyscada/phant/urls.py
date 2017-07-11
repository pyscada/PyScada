# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [
    # Public pages
    url(r'^input/(.{1,20})/$', views.phant_input, {'json_response': False}, name="input-plain/text", ),
    url(r'^input/(.{1,20}).json$', views.phant_input, {'json_response': True}, name="input-application/json", ),
]
