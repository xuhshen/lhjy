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
from examples import views

from rest_framework.urlpatterns import format_suffix_patterns


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'strategyuser', views.Strategy_userViewSet)
# router.register(r'record', views.RecordViewSet)

# urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns = [
    url(r'^examples/', include('examples.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^buy/$', views.RecordViewSet.as_view()),
    url(r'^sell/$', views.RecordViewSet.as_view()),
    url(r'^cancel/(?P<pk>[0-9]+)/$', views.RecordUpdateViewSet.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]


