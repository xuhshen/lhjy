from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Strategy_user,Capitalaccount,Action,Status,Record,Stock
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order2securities,cancel_order2securities


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

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"
    
class Strategy_userSerializer(serializers.ModelSerializer):
    capitalaccount = CapitalaccountSerializer()
    user = UserSerializer()
    hold_position = StockSerializer(source='get_stocks', many=True)
    
    class Meta:
        model = Strategy_user
        fields = ('user', 'capitalaccount', 'total_money','enable_money','hold_position')

class RecordOrderSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.CharField(source="status.status",read_only=True)
    action = serializers.CharField(source="action.name")
    user = serializers.CharField(source="user.user.username",read_only=True)
    account = serializers.CharField(source="account.account_name",read_only=True)
    class Meta:
        model = Record
        fields = ('id','user','account','status','action','code','name','number','price','trademoney','tradenumber','market_price','market_ticket','create_time')
        read_only_fields=("trademoney",'tradenumber','name','market_ticket',)
        
    def create(self, validated_data):
        user=Strategy_user.objects.get(user__username=self.context["request"].user)
        status=Status.objects.get(status="pending")
        try:
            action=Action.objects.get(name=validated_data.get("action")["name"])
        except:
            raise ValidationError({"action":"this field value incorrect!"})
        account=user.capitalaccount
        
        market_ticket,price = order2securities([validated_data,account.account_name])
        
        validated_data.update(user=user)
        validated_data.update(status=status)
        validated_data.update(action=action)
        validated_data.update(account=account)
        validated_data.update(market_ticket=market_ticket)
        validated_data.update(price=price)

        return Record.objects.create(**validated_data)
    
class RecordCancelSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.CharField(source="status.status",read_only=True)
    action = serializers.CharField(source="action.name",read_only=True)
    user = serializers.CharField(source="user.user.username",read_only=True)
    account = serializers.CharField(source="account.account_name",read_only=True)
    class Meta:
        model = Record
        fields = ('id','user','account','status','action','code','name','number','price','trademoney','tradenumber','market_price','market_ticket','create_time')
        read_only_fields=("trademoney",'tradenumber','name','code','number','price','market_price','market_ticket',)

    def update(self, instance, validated_data):
        instance.status = Status.objects.get(status="cancel")
        instance.save()
        return instance








    
    