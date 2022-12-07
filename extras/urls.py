"""PyScadaServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from pkgutil import iter_modules
from importlib.util import find_spec
import pyscada


def list_submodules(module):
    submodules = []
    for submodule in iter_modules(module.__path__):
        submodules.append(submodule)
    return submodules


urlpatterns = [
    url(r'^admin/', admin.site.urls),
]


lsm = list_submodules(pyscada)
for m in lsm:
    try:
        if m.name != 'hmi' and find_spec('pyscada.' + m.name + '.urls'):
            urlpatterns += [
                url(r'^', include('pyscada.' + m.name + '.urls')),
            ]
    except:
        pass

try:
    import django_cas_ng.views
    urlpatterns += [
        url(r'^accounts/CASlogin/$', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        url(r'^accounts/logout$', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
        url(r'^accounts/callback$', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
    ]
except ImportError:
    pass


urlpatterns += [
    url(r'^', include('pyscada.hmi.urls')),
]
