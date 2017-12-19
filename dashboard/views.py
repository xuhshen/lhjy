from django.shortcuts import render
from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from app.models import *
from app.serializers import *
from .serializers import IndexSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework import permissions

class index(generics.GenericAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
#     permission_classes = (permissions.IsAdminUser,)
     
    queryset = CapitalAccount.objects.all()
    serializer_class = IndexSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        print (serializer.data)
        return render(request, 'index.html',{"data":serializer.data})

 
def product(request):
    return render(request, 'product.html')

def holdlist(request):
    return render(request, 'holdlist.html')


