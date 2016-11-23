# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views

urlpatterns = [
    # Public pages
    url(r'^input/(.{1,20})/$', views.input ,{'json_response': False},name="input-plain/text",),
    url(r'^input/(.{1,20}).json$', views.input ,{'json_response': True},name="input-application/json",),
]
