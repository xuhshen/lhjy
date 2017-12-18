from django.shortcuts import render
from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from app.models import *
from app.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework import permissions



def index(request):
    return render(request, 'index.html')
 
def product(request):
    return render(request, 'product.html')

def holdlist(request):
    return render(request, 'holdlist.html')

def list2(request):
    return render(request, '会员列表.html')

def list3(request):
    return render(request, '库存管理.html')

def list4(request):
    return render(request, '商品分类.html')

def list5(request):
    return render(request, '信息通知.html')


