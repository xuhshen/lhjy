from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='product'),
    url(r'^product/(?P<project>.+)/$', views.product, name='product'),
    url(r'^value/(?P<account>[0-9]+)/$', views.value,name='value'),
    url(r'^holdlist/(?P<account>[0-9]+)/$', views.holdlist, name='holdlist')
#     url(r'^holdlist/(?P<account>[0-9]+)/$', views.holdlist.as_view())
#     url(r'^holdlist/$', views.holdlist, name='holdlist'),
]