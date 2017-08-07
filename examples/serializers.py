from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Strategy_user,Capitalaccount,Action,Status,Record


class ActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Action
        fields = ('name',)

class StatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Status
        fields = ('status',)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class CapitalaccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Capitalaccount
        fields = ('account_name', )

class Strategy_userSerializer(serializers.HyperlinkedModelSerializer):
    capitalaccount = CapitalaccountSerializer()
    user = UserSerializer()
    class Meta:
        model = Strategy_user
        fields = ('user', 'capitalaccount', 'total_money','enable_money')

class RecordSerializer(serializers.HyperlinkedModelSerializer):
    status = StatusSerializer()
    action = ActionSerializer()
    class Meta:
        model = Record
        fields = ('status','action','code','name','number','money','trademoney','tradenumber')
        

