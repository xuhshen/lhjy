from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Strategy_user,Capitalaccount,Action,Status,Record,Stock,Membership,Dailyinfo
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order2securities,cancel_order2securities
from lhjy.settings import TESTING_ACCOUNT
import time,json


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
        fields = ('id','user','account','status','action','code','name','number','price',
                  'trademoney','tradenumber','market_price','market_ticket','create_time',
                  "lastupdate_time")
        read_only_fields=("trademoney",'tradenumber','name','market_ticket',)
        
    def create(self, validated_data):
        
        try:
            action=Action.objects.get(name=validated_data.get("action")["name"])
        except:
            raise ValidationError({"action":"this field value incorrect!"})
        
        user=Strategy_user.objects.get(user__username=self.context["request"].user)
        account=user.capitalaccount 
        stock_user = user.user
        
        #账户资金检查和股票余量检查
        if validated_data.get("action")["name"] == "sell" :
            try:
                stock = Stock.objects.get(user=stock_user,code=validated_data.get("code"))
            except:
                raise ValidationError({"message":"you do not hold this stock"})
            
            new_number = stock.number-validated_data.get("number")-stock.frozennumber
            if new_number < 0:
                raise ValidationError({"message":"you do not hold so many stock"})
            stock.frozennumber += validated_data.get("number")
        else:
            user.enable_money -= validated_data.get("price")*validated_data.get("number")
            account.enable_money -= validated_data.get("price")*validated_data.get("number")
            if user.enable_money < 0:
                raise ValidationError({"message":"you do not have so many money"})
        
        if str(self.context["request"].user) == TESTING_ACCOUNT:
            status = Status.objects.get(status="deal")
            market_ticket = str(time.time()) # 为测试账户生成一个随机数委托单
            
            validated_data.update(trademoney=validated_data.get("price"))
            validated_data.update(tradenumber=validated_data.get("number"))
            
            if validated_data.get("action")["name"] == "buy":
                stock_object = Stock.objects.get_or_create(user=stock_user,code=validated_data.get("code"))
                
                stock = stock_object[0]
                stock.cost_price = (stock.cost_price*stock.number + \
                    validated_data.get("number")*validated_data.get("price"))/(validated_data.get("number")+stock.number)
                stock.number += validated_data.get("number")
                stock.market_price = validated_data.get("price")
                stock.market_value = stock.number*stock.market_price
                
                if stock_object[1]:
                    Membership.objects.create(strategy_user=user,stock=stock)
            else:
                if new_number == 0:
                    stock.cost_price = 0
                else:
                    stock.cost_price = (stock.cost_price*stock.number - \
                        validated_data.get("number")*validated_data.get("price"))/(new_number)
                stock.frozennumber -= validated_data.get("number")
                stock.number = new_number
                stock.market_price = validated_data.get("price")
                stock.market_value = stock.number*stock.market_price
                user.enable_money += validated_data.get("price")*validated_data.get("number")
                account.enable_money += validated_data.get("price")*validated_data.get("number")
        else:
            status=Status.objects.get(status="pending")
            market_ticket,price = order2securities([validated_data,account.account_name])
            validated_data.update(price=price)
        
        if validated_data.get("action")["name"] == "sell" :
            stock.save()
        
        validated_data.update(user=user)
        validated_data.update(status=status)
        validated_data.update(action=action)
        validated_data.update(account=account)
        validated_data.update(market_ticket=market_ticket)
        account.save()
        user.save()
        return Record.objects.create(**validated_data)
    
class RecordCancelSerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.CharField(source="status.status",read_only=True)
    action = serializers.CharField(source="action.name",read_only=True)
    user = serializers.CharField(source="user.user.username",read_only=True)
    account = serializers.CharField(source="account.account_name",read_only=True)
    class Meta:
        model = Record
        fields = ('id','user','account','status','action','code','name','number','price',
                  'trademoney','tradenumber','market_price','market_ticket','create_time',
                  'lastupdate_time')
        read_only_fields=("trademoney",'tradenumber','name','code','number','price','market_price','market_ticket',)

    def update(self, instance, validated_data):
        '''更新 record 状态，更新账户资金，更新record 交易资金
        '''
        if instance.status.status in ["cancel","deal"]: 
            return instance
        
        #更新revord状态
        instance.status = Status.objects.get(status="cancel")
        
        data = cancel_order2securities(instance.market_ticket)
        
        #更新账户资金，解冻资金
        self.update_account(data,instance)  
        
        #更新record 成交部分数量和资金
        instance.trademoney = data["trademoney"]
        instance.tradenumber = data["tradenumber"]
        
        instance.save()
        
        return instance
    
    def update_account(self,data,instance):
        '''更新账户资金
        '''
        account =  Strategy_user.objects.get(user__username=instance.user.user.username)
        
        if instance.action.name == "buy":
            account.enable_money += instance.price*instance.number-data["trademoney"]*data["tradenumber"]
            stock = Stock.objects.get_or_create(user=instance.user.user,code=instance.code)[0]
            stock.cost_price = (stock.cost_price*stock.number + \
                    data["tradenumber"]*data["trademoney"])/(data["tradenumber"]+stock.number)
            stock.number += data["tradenumber"]
        elif instance.action.name == "sell":
            stock = Stock.objects.get(user=instance.user.user,code=instance.code)
            stock.cost_price = (stock.cost_price*stock.number - \
                    data["tradenumber"]*data["trademoney"])/(stock.number-data["tradenumber"])
            stock.frozennumber -= instance.number
            stock.number -= data["tradenumber"]
            account.enable_money += data["trademoney"]*data["tradenumber"]
        account.save()
        stock.save()


class RecordQuerySerializer(serializers.HyperlinkedModelSerializer):
    status = serializers.CharField(source="status.status")
    action = serializers.CharField(source="action.name",read_only=True)
    user = serializers.CharField(source="user.user.username",read_only=True)
    account = serializers.CharField(source="account.account_name",read_only=True)
    class Meta:
        model = Record
        fields = ('id','user','account','status','action','code','name','number','price',
                  'trademoney','tradenumber','market_price','market_ticket','create_time',
                  'lastupdate_time')
        read_only_fields=('code','number','market_ticket','price',)

    def update(self, instance, validated_data):
        if validated_data.get("status"):
            instance.status = Status.objects.get(status=validated_data.get("status")["status"])
        instance.name = validated_data.get("name",instance.name)
        instance.trademoney = validated_data.get("trademoney",instance.trademoney)
        instance.tradenumber = validated_data.get("tradenumber",instance.tradenumber)
        
        instance.save()
        return instance


class DailyLiquidationSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.user.username",read_only=True)
    account = serializers.CharField(source="account.account_name",read_only=True)
    
    class Meta:
        model = Dailyinfo
        fields = "__all__"
        read_only_fields=("holdlist",'money','marketvalue',)

    def create(self, validated_data):
        user = Strategy_user.objects.get(user__username=self.context["request"].user)
        account = user.capitalaccount
        stocks = user.get_stocks()
        holdlist = json.dumps({stock.code:stock.number for stock in stocks })
        money = user.enable_money  
        marketvalue = money + sum([stock.market_value for stock in stocks])
        
        validated_data.update(user=user)
        validated_data.update(account=account)
        validated_data.update(holdlist=holdlist)
        validated_data.update(money=money)
        validated_data.update(marketvalue=marketvalue)
        
        return Dailyinfo.objects.create(**validated_data)
    
    