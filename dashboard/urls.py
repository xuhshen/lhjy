from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list/$', views.list, name='list'),
    url(r'^list1/$', views.list1, name='list1'),
    url(r'^list2/$', views.list2, name='list2'),
    url(r'^list3/$', views.list3, name='list3'),
    url(r'^list4/$', views.list4, name='list4'),
    url(r'^list5/$', views.list5, name='list5'),
    
]