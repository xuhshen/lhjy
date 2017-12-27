from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order,cancel

# class CapitalAccountSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CapitalAccount
#         fields = "__all__"
# 
# 
# class HoldCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = HoldCategory
#         fields = "__all__"
# 
# class StrategyUserSerializer(serializers.ModelSerializer):
#     holdlist = HoldCategory()
#     
#     class Meta:
#         model = StrategyUser
#         fields = "__all__"
# 
# class RecordSerializer(serializers.ModelSerializer):
#     action = serializers.CharField(write_only=True)
#     number = serializers.FloatField(write_only=True)
#     stock = serializers.CharField(write_only=True)
#     class Meta:
#         model = Record
#         fields = "__all__"
#         read_only_fields = ("strategy_account","trade_status","already_trade_money",
#                             "already_trade_number","waiting_trade_money",
#                             "waiting_trade_number","trade_action","trade category",
#                             "pretrade_number","pretrade_money","trade_category","ticket")
# 
#     def validate(self, attrs):
#         validated_data = {}
#         try:
#             action = Action.objects.get(name=attrs.get("action"))
#         except:
#             actionlist = [i.name for i in Action.objects.all()]
#             raise ValidationError({"action":"this field value incorrect!",
#                                    "options":actionlist})
#         try:
#             category = Category.objects.get(code=attrs.get("stock"))
#         except:
#             raise ValidationError({"交易品种错误":"交易品种不存在，请确认交易品种代码",})
#         
#         number = attrs.get("number",0)
#         is_market_price = attrs.get("is_market_price",False)
#         if number<=0:
#             raise ValidationError({"交易数量错误":"交易数量必须大于0",})
#         
#         if is_market_price:
#             price = category.current_price
#         else:
#             price = attrs.get("price",0)
#         
#         if price <=0:
#             raise ValidationError({"交易价格错误":"交易价格必须大于0",})    
#         
#         strategy_user = StrategyUser.objects.get(user__username=self.context["request"].user)
#         
#         
#         validated_data["trade_action"] = action
#         validated_data["trade_category"] = category
#         validated_data["strategy_account"] = strategy_user
#         validated_data["trade_status"],_ = Status.objects.get_or_create(status="委托")
#         validated_data["is_market_price"] = is_market_price
#         
#         validated_data["price"] = price
#         validated_data["pretrade_number"] = number
#         validated_data["pretrade_money"] = price*number
# 
#         return validated_data
#     
#     
#     def create(self, validated_data):
#         strategy_account = validated_data["strategy_account"]
#         
#         if validated_data.get("trade_action").name == "买入":
#             strategy_account.enable_money -= validated_data["pretrade_money"]
#             
#             if strategy_account.enable_money <=0:
#                 raise ValidationError({"错误类型":"资金不足",})
#             
#             strategy_account.capitalaccount.enable_money -= validated_data["pretrade_money"]
#             
#             ticket,_ = order(validated_data)
#             
#             strategy_account.capitalaccount.save()
#             strategy_account.save()
#         else:
#             category = validated_data["trade_category"]
#             try:
#                 hold_category = strategy_account.holdlist.filter(code=category)
#                 hold_category.frozen_number -= validated_data["pretrade_number"]
#                 if hold_category.frozen_number <0:
#                     raise ValidationError({"错误类型":"标的数量不足",})
#             except:
#                 raise ValidationError({"错误类型":"未持有该标的物，禁止卖出",})
#             
#             ticket,_ = order(validated_data)
#         
#         validated_data["ticket"] = ticket
#             
#         return Record.objects.create(**validated_data) 
#     
#     
# class RecordCancelSerializer(serializers.ModelSerializer):    
#     trade_status = serializers.CharField(source="trade_status.status",read_only=True)
#     
#     class Meta:
#         model = Record
#         fields = "__all__"
#         
#         read_only_fields = ("strategy_account","trade_status","already_trade_money",
#                             "already_trade_number","waiting_trade_money",
#                             "waiting_trade_number","trade_action","trade category",
#                             "pretrade_number","pretrade_money","trade_category",
#                             "is_market_price","price")
#     
#     def update(self, instance, validated_data):
#         '''不更新任何状态，只下发cancel 命令
#         '''
#         if instance.trade_status.status in ["撤单","成交"]:
#             pass
#         else:
#             trade_status,_ = Status.objects.get_or_create(status="撤单")
#             instance.trade_status = trade_status
#             res = cancel(instance.ticket,instance.trade_category.code)
#         
#         holdrecord = instance.strategy_account.holdlist.get(code = instance.trade_category)
#             
#         if instance.trade_action.name == "买入":
#             holdrecord.hold_number += res["tradenumber"] - instance.already_trade_number
#             
#             release_money = instance.pretrade_money - res["tradenumber"]*res["tradeprice"]
#             
#             instance.strategy_account.capitalaccount.enable_money += release_money    
#             instance.strategy_account.enable_money += release_money
#             
#             
#         elif instance.trade_action.name == "卖出":
#             holdrecord.frozen_number -= instance.already_trade_number - res["tradenumber"]
#             instance.strategy_account.enable_money += res["tradeprice"]*res["tradenumber"] - instance.already_trade_money 
#             instance.strategy_account.capitalaccount.enable_money += res["tradeprice"]*res["tradenumber"] - instance.already_trade_money 
#         
#         instance.waiting_trade_money = 0
#         instance.waiting_trade_number = 0
#         instance.already_trade_number = res["tradenumber"]
#         instance.already_trade_money = res["tradenumber"]*res["tradeprice"] 
#         
#         holdrecord.save()
#         instance.strategy_account.save()
#         instance.strategy_account.capitalaccount.save()
#         instance.save()
#         
#         return instance
#         
#  
# class RecordQuerySerializer(serializers.ModelSerializer):
#     deal_money = serializers.FloatField(write_only=True)
#     deal_number = serializers.FloatField(write_only=True)
# #     current_price = serializers.FloatField(write_only=True)
#     
#     trade_action = serializers.CharField(source="trade_action.name",read_only=True)
#     trade_category = serializers.CharField(source="trade_category.code",read_only=True)
#     account = serializers.CharField(source="strategy_account.capitalaccount.account_name",read_only=True)
#     trade_status = serializers.CharField(source="trade_status.status",read_only=True)
#     
#     class Meta:
#         model = Record
#         fields = "__all__"
#         read_only_fields=('pretrade_money','pretrade_number',
#                           'is_market_price','waiting_trade_money',
#                           'waiting_trade_number','strategy_account',
#                           'trade_action','trade_category','trade_status',
#                           'ticket','price','already_trade_money',
#                           'already_trade_number',
#                           )
#  
#     def validate(self, attrs):
#         validated_data = {}
#         validated_data["deal_money"] = attrs.get("deal_money",-1)
#         validated_data["deal_number"] = attrs.get("deal_number",-1)
# #         validated_data["current_price"] = attrs.get("current_price",-1)
#         
#         if validated_data["deal_money"] <0:
#             raise ValidationError({"error":"成交金额错误"})
#         
#         if validated_data["deal_number"] <0:
#             raise ValidationError({"error":"成交数量输错"})
#         
# #         if validated_data["current_price"] <0:
# #             raise ValidationError({"error":"市场价没传或者小于0"})
#         
#         
#         return validated_data
#  
#     def update(self, instance, validated_data):
# #         instance.trade_category.current_price = validated_data["current_price"]
# #         instance.trade_category.save()
#         
#         if instance.already_trade_number == validated_data["deal_number"]:
#             return instance
#         
#         print (validated_data["deal_number"])
#         if validated_data["deal_number"] == instance.pretrade_number:
#             instance.trade_status,_ = Status.objects.get_or_create(status = "成交")
#         elif validated_data["deal_number"] > 0:
#             instance.trade_status,_ = Status.objects.get_or_create(status = "部分成交")
#         
#         increment_mongey = validated_data["deal_money"] - instance.already_trade_money
#         increment_number = validated_data["deal_number"] - instance.already_trade_number
#         
#         instance.already_trade_money = validated_data["deal_money"]
#         instance.already_trade_number = validated_data["deal_number"]
#         
#         instance.waiting_trade_money -= increment_mongey
#         instance.waiting_trade_number -= increment_number
#         
#         hold_category,_ = instance.strategy_account.holdlist.get_or_create(code=instance.trade_category)
#         
#         if instance.trade_action.name == "买入":
#             hold_category.hold_number += increment_number
#             
#         elif instance.trade_action.name == "卖出":
#             hold_category.hold_number -= increment_number
#             hold_category.frozen_number -= increment_number
#             instance.strategy_account.enable_money += increment_mongey
#             instance.strategy_account.capitalaccount.enable_money += increment_mongey 
#             
#             instance.strategy_account.capitalaccount.save()
#             instance.strategy_account.save()
#             
#         hold_category.save()
#         instance.save()
#         
#         return instance


#     
#     