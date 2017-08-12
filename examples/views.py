from django.shortcuts import render

from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer,Strategy_userSerializer,RecordSerializer,RecordCancelSerializer
from .models import Strategy_user,Record

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import backendupdate, order2securities

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
                  mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    
    serializer_class = RecordSerializer
    
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
        
        ticket = order2securities(serializer.data)
        Record.objects.filter(id=serializer.data.get("id")).update(market_ticket=ticket)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class RecordUpdateViewSet(mixins.UpdateModelMixin,
                  generics.GenericAPIView):
    serializer_class = RecordCancelSerializer
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
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
