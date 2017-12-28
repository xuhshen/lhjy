from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from rest_framework.exceptions import ErrorDetail, ValidationError
from .dealer import order,cancel

    
class AccountSerializer(serializers.ModelSerializer):
    market = serializers.JSONField(write_only=True)
    holdlist = serializers.JSONField(write_only=True)
    tickets = serializers.JSONField(write_only=True)
    class Meta:
        model = Account
        fields = ("market","holdlist","tickets",)

    def validate(self, attrs):
        validated_data = {}
        validated_data["market"] = attrs.get("market",None)
        validated_data["holdlist"] = attrs.get("holdlist",[])
        validated_data["tickets"] = attrs.get("tickets",[])
         
        return validated_data
  
    def update(self, instance, validated_data):
        recorddata = {"account":instance,
                      "rest_capital":validated_data["market"].get(u"资金余额",-1),
                      "enable_capital":validated_data["market"].get(u"可用资金",-1),
                      "frozen_capital":validated_data["market"].get(u"冻结资金",-1),
                      "market_value":validated_data["market"].get(u"最新市值",-1),
                      "total_assets":validated_data["market"].get(u"总资产",-1),
                      "profit_loss":validated_data["market"].get(u"浮动盈亏",-1),
                      "preferred_capital":validated_data["market"].get(u"可取资金",-1),
                      "margin_selling_capital":validated_data["market"].get(u"融券卖出资金",-1),
                      "counters_bought_number":validated_data["market"].get(u"取柜台可买数量",-1),}
        slr,_ = StockLatestRecord.get_or_create(account=instance)
        slr.update(**recorddata)
        slr.save()
        
        for i in validated_data["holdlist"]:
            shl,_ = StockHoldList.get_or_create(account=instance,code=i[u"证券代码"])
            i_data = {"name":i[u"证券名称"],
                      "number":i[u"证券数量"],
                      "enable_number":i[u"可卖数量"],
                      "buy_price":i[u"成本价"],
                      "cost":i[u"盈亏成本价"],
                      "current_price":i[u"当前价"],
                      "market_value":i[u"最新市值"],
                      "profit_loss":i[u"浮动盈亏"],
                      "profit_loss_rate":i[u"盈亏比例"],
                      "buy_financing_balance":i[u"融资买入证券实时余额"],
                      "rest_buy_financing":i[u"融资买入余额"],
                      "enable_buy_financing":i[u"融资买入可用"],
                      "value_rate":i[u"个股资产比例"],
                      }
            shl.update(**i_data)
            shl.save()
        
        for t in validated_data["tickets"]:
            st,_ = StockTicket.get_or_create(account=instance,code=t[u"证券代码"],order_date=t[u"委托日期"])
            t_data = {"order_time":t[u"委托时间"],
                      "name":t[u"证券名称"],
                      "action":t[u"买卖标志"],
                      "order_price":t[u"委托价格"],
                      "order_number":t[u"委托数量"],
                      "order_ticket":t[u"委托编号"],
                      "deal_number":t[u"成交数量"],
                      "deal_money":t[u"成交金额"],
                      "cancel_number":t[u"撤单数量"],
                      "cancel_mark":t[u"撤单标志"],
                      }
            st.update(**t_data)
            st.save()
        return instance
    
