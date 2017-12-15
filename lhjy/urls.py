"""lhjy URL Configuration

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
from django.conf.urls import url,include
from django.contrib import admin

from rest_framework import routers
from app import views
from rest_framework.authtoken import views as vs
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'strategyuser', views.StrategyUserViewSet)

urlpatterns = [
    url(r'^app/', include('app.urls')),
    url(r'^dashboard/', include('dashboard.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^order/$', views.RecordOrderViewSet.as_view()),
    url(r'^account/$', views.CapitalAccountViewSet.as_view()),
    url(r'^cancel/(?P<pk>[0-9]+)/$', views.RecordCancelViewSet.as_view()),
    url(r'^record/(?P<pk>[0-9]+)/$', views.RecordQueryViewSet.as_view()),
]





