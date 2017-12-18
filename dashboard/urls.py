from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^product/$', views.product, name='product'),
    url(r'^holdlist/$', views.holdlist, name='holdlist'),
    url(r'^list2/$', views.list2, name='list2'),
    url(r'^list3/$', views.list3, name='list3'),
    url(r'^list4/$', views.list4, name='list4'),
    url(r'^list5/$', views.list5, name='list5'),
    
]