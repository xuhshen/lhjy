from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='product'),
    url(r'^product/$', views.product.as_view()),
    url(r'^value/(?P<account>[0-9]+)/$', views.value,name='value'),
    url(r'^holdlist/$', views.holdlist.as_view())
#     url(r'^holdlist/$', views.holdlist, name='holdlist'),
]