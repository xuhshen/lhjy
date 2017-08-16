from django.shortcuts import render

from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer,Strategy_userSerializer,RecordOrderSerializer,RecordCancelSerializer
from .models import Strategy_user,Record

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order2securities,cancel_order2securities
from rest_framework import permissions

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAdminUser,)
    
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    

class Strategy_userViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAdminUser,)
    
    queryset = Strategy_user.objects.all()
    serializer_class = Strategy_userSerializer
    
#     def get(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
    
    
class RecordOrderViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    
    serializer_class = RecordOrderSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        today = date.today()
        queryset = Record.objects.filter(user__user=self.request.user,create_time__gte=today)
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        self.update_account(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update_account(self,data):
        if data["action"] == "buy":
            account =  Strategy_user.objects.get(user__username=data["user"])
            account.enable_money -= data["price"]*data["number"]
            account.save()
    

class RecordCancelViewSet(mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    serializer_class = RecordCancelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        today = date.today()
        queryset = Record.objects.filter(user__user=self.request.user,create_time__gte=today)
        return queryset
    
    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        back = cancel_order2securities(serializer.data)
        if back:
            self.update_account(serializer.data)
        
        return Response(serializer.data)

    def update_account(self,data):
        account =  Strategy_user.objects.get(user__username=data["user"])
        account.enable_money += data["price"]*data["number"]-data["trademoney"]*data["tradenumber"]
        account.save()


