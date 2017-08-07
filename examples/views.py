from django.shortcuts import render

from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer,Strategy_userSerializer,RecordSerializer
from .models import Strategy_user,Record

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from rest_framework import mixins
from rest_framework import generics





class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class Strategy_userViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Strategy_user.objects.all()
    serializer_class = Strategy_userSerializer
    


class RecordViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    
#     queryset = Record.objects.all()
    serializer_class = RecordSerializer
    
    def get(self, request, *args, **kwargs):
        self.queryset = Record.objects.all()
        print (request.user)
#         self.queryset = Record.objects.all()
# #         queryset = Record.objects.all()
#         queryset = self.filter_queryset(self.get_queryset())
# #         queryset = self.filter_queryset(queryset)
# 
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
# 
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
        return  self.list(request, *args, **kwargs)
# 
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)







