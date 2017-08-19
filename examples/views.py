from django.shortcuts import render

from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Strategy_user,Record,Status,Dailyinfo
from .serializers import UserSerializer,Strategy_userSerializer,RecordOrderSerializer,\
                        RecordCancelSerializer,RecordQuerySerializer,DailyLiquidationSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order2securities,cancel_order2securities,queryfromsecurities
from rest_framework import permissions
from lhjy.settings import TESTING_ACCOUNT

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAdminUser,)
    
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

class All_Strategy_userViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAdminUser,)
    
    queryset = Strategy_user.objects.all()
    serializer_class = Strategy_userSerializer   

class Strategy_userViewSet(mixins.ListModelMixin,
                  generics.GenericAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = Strategy_userSerializer
    
    def get_queryset(self):
        queryset = Strategy_user.objects.filter(user__username=self.request.user)
        return queryset
    
    def get(self, request, *args, **kwargs): 
        return self.list(self, request, *args, **kwargs)
        
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
        '''获取当日委托单新，如果是测试账户，跳过同步
                        同时和券商同步未完成委托单状态，但不保存
        '''
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        if request.user != TESTING_ACCOUNT:
            n_data = self.sync_account(serializer.data)
        else:
            return Response(serializer.data)
        return Response(n_data)

    def post(self, request, *args, **kwargs):
        '''添加record记录，更新账户可用资金
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    def sync_account(self,records):
        '''同步未完成委托单信息
        '''
        rst = queryfromsecurities(None)
        if not rst: return records 

        for record in records:
            if record.get("status") not in ["deal","cancel"]:
                ticket = rst[record.get("market_ticket")]
                record.update(trademoney = ticket["trademoney"])
                record.update(tradenumber = ticket["tradenumber"])
                record.update(status = ticket["status"])
        return  records   

class RecordCancelViewSet(mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    serializer_class = RecordCancelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        today = date.today()
        queryset = Record.objects.filter(user__user=self.request.user,create_time__gte=today)
        return queryset
    
    def post(self, request, *args, **kwargs):
        '''更新 record 状态，更新账户资金，更新record 交易资金
        '''
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

class RecordQueryViewSet(mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    serializer_class = RecordQuerySerializer
    permission_classes = (permissions.IsAdminUser,)
    
    def get_queryset(self):
        today = date.today()
        queryset = Record.objects.filter(status__status__in=["pending","partial deal"],create_time__gte=today)
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data) 

class DailyLiquidationViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              generics.GenericAPIView):
    
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = DailyLiquidationSerializer

    def get_queryset(self):
        queryset = Dailyinfo.objects.filter(user__user=self.request.user)
        return queryset
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



