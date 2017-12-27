from django.shortcuts import render
 
from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import *
from .serializers import *
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework import permissions

# class OrderViewSet(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   mixins.UpdateModelMixin,
#                   generics.GenericAPIView):
#      
#     serializer_class = RecordSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#      
#     def get_queryset(self):
#         today = date.today()
#         queryset = Record.objects.filter(strategy_account__user=self.request.user,create_time__gte=today)
#         return queryset
#      
#     def get(self, request, *args, **kwargs):
#         '''
#         '''
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#  
#         return Response(serializer.data)
#  
#     def post(self, request, *args, **kwargs):
#         '''添加record记录，更新账户可用资金
#         '''
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#          
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
# 
# class CancelViewSet(mixins.UpdateModelMixin,
#                   generics.GenericAPIView):
#     serializer_class = RecordCancelSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#      
#     def get_queryset(self):
#         today = date.today()
#         queryset = Record.objects.filter(strategy_account__user=self.request.user,create_time__gte=today)
#         return queryset
#      
#     def post(self, request, *args, **kwargs):
#         '''更新 record 状态，更新账户资金，更新record 交易资金
#         '''
#         return  self.update(request,*args, **kwargs)
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# ###################################################################################
# class RecordOrderViewSet(mixins.ListModelMixin,
#                   mixins.CreateModelMixin,
#                   mixins.UpdateModelMixin,
#                   generics.GenericAPIView):
#      
#     serializer_class = RecordSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#      
#     def get_queryset(self):
#         today = date.today()
#         queryset = Record.objects.filter(strategy_account__user=self.request.user,create_time__gte=today)
#         return queryset
#      
#     def get(self, request, *args, **kwargs):
#         '''
#         '''
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#  
#         return Response(serializer.data)
#  
#     def post(self, request, *args, **kwargs):
#         '''添加record记录，更新账户可用资金
#         '''
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#          
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
# 
# 
# class RecordCancelViewSet(mixins.UpdateModelMixin,
#                   generics.GenericAPIView):
#     serializer_class = RecordCancelSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#      
#     def get_queryset(self):
#         today = date.today()
#         queryset = Record.objects.filter(strategy_account__user=self.request.user,create_time__gte=today)
#         return queryset
#      
#     def post(self, request, *args, **kwargs):
#         '''更新 record 状态，更新账户资金，更新record 交易资金
#         '''
#         return  self.update(request,*args, **kwargs)
#  
# class RecordQueryViewSet(mixins.UpdateModelMixin,
#                   generics.GenericAPIView):
#     serializer_class = RecordQuerySerializer
#     permission_classes = (permissions.IsAdminUser,)
# #     search_fields = ("id",)
# #     lookup_field = "id"
#     '''供管理员账户定时更新后台数据，
#     '''
#      
#     def get_queryset(self):
#         today = date.today()
#         queryset = Record.objects.filter(trade_status__status__in=["部分成交","委托"],create_time__gte=today)
#         return queryset
#      
#     def get(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#      
#     def post(self, request, *args, **kwargs):
#         return self.update(request,*args, **kwargs)
# 
# 
# 
# class StrategyUserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     permission_classes = (permissions.IsAdminUser,)
#      
#     queryset = StrategyUser.objects.all()
#     serializer_class = StrategyUserSerializer
# 
# class CapitalAccountViewSet(generics.ListAPIView):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = CapitalAccount.objects.all()
#     filter_fields = ("account_name",) 
#     
#     serializer_class = CapitalAccountSerializer
 
# class DailyLiquidationViewSet(mixins.ListModelMixin,
#                               mixins.CreateModelMixin,
#                               generics.GenericAPIView):
#     
#     permission_classes = (permissions.IsAdminUser,)
#     serializer_class = DailyLiquidationSerializer
# 
#     def get_queryset(self):
#         queryset = Dailyinfo.objects.filter(user__user=self.request.user)
#         return queryset
#     
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)
#     
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
# 


