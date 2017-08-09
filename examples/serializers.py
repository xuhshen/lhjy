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
    status = serializers.CharField(source="status.status",read_only=True)
    action = serializers.CharField(source="action.name")
    user = serializers.CharField(source="user.user.username",read_only=True)
    class Meta:
        model = Record
        fields = ('id','user','status','action','code','name','number','price','trademoney','tradenumber','create_time')
        
    def create(self, validated_data):
        
        user=Strategy_user.objects.get(user__username=self.context["request"].user)
        status=Status.objects.get(status="pending")
        action=Action.objects.get(name=validated_data.get("action")["name"])
        account=user.capitalaccount
        
        validated_data.update(user=user)
        validated_data.update(status=status)
        validated_data.update(action=action)
        validated_data.update(account=account)
        
        return Record.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.email)
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.trademoney = validated_data.get('trademoney', instance.trademoney)
        instance.tradenumber = validated_data.get('tradenumber', instance.tradenumber)
        instance.save()
        return instance
    
    
    