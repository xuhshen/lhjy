from django.shortcuts import render
from django.http import HttpResponse,Http404
from django.contrib.auth.models import User
from rest_framework import viewsets
from app.models import *
from .serializers import IndexSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from datetime import date
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework import permissions
import collections
import pandas as pd
import math

def product(request,project):
    accounts = Account.objects.filter(project=Project.objects.get(name=project)).all()
    rst = {}
    temp_all = {"account":{},"change":{}}
    dct = {"股票":0,"期货":0,"固收":0,"对冲":0}
    for acc in accounts:
        dct[acc.type] += 1
        temp = {}
        changehistory = Moneyhistory.objects.filter(account=acc).all()
        initial = 0
        money = acc.total_assets
        rest = acc.rest_capital
        earnest = acc.earnest_capital
        market_value = acc.market_value
        
        for i in changehistory:
            initial += i.money
        rst[acc.name] = collections.OrderedDict()
        rst[acc.name]["account"] = acc.account
        rst[acc.name]["账户名称"] = "{}_{}_{}".format(project,acc.type,dct[acc.type])
        rst[acc.name]["起始时间"] = acc.starttime.strftime('%Y-%m-%d')
        rst[acc.name]["持仓个数"] = 0
        rst[acc.name]["持仓比例"] = 0
        rst[acc.name]["今日收益"] = 0
        rst[acc.name]["累计收益"] = 0
        rst[acc.name]["最新净值"] = 0
        rst[acc.name]["账户市值"] = "{:.1f}".format(money)
        
        if acc.type in ["股票","固收"]:
            rst[acc.name]["持仓个数"] = StockHoldList.objects.filter(account=acc,number__gt=0).count()
            rst[acc.name]["持仓比例"] = "{:.2f}%".format(100*(market_value/money))
            temp["account"] = {i.date:i.total_assets for i in StockHistory.objects.filter(account=acc)}
        else:
            rst[acc.name]["持仓个数"] = FuturesHoldList.objects.filter(account=acc,number__gt=0).count()
            rst[acc.name]["持仓比例"] = "{:.2f}%".format(100*earnest/money)
            temp["account"] = {i.date:i.total_assets for i in FuturesHistory.objects.filter(account=acc)}
        
        temp["change"] = {i.date:i.money for i in Moneyhistory.objects.filter(account=acc)}
            
        rst[acc.name]["累计收益"] = "{:.1f}".format(money - initial)
        
        for k in temp.keys():
            for dt in temp[k].keys():
                if temp_all[k].__contains__(dt):
                    temp_all[k][dt] += temp[k][dt]
                else:
                    temp_all[k][dt] = temp[k][dt]
                 
        df = pd.DataFrame(temp)
        df.ix[0,"initial"] = df.ix[0,"account"]
        df.fillna(0,inplace=True)
        filt = df["initial"]==0
        df.loc[filt,"initial"] = 1+df.loc[filt,"change"]/(df.loc[filt,"account"]-df.loc[filt,"change"]) 
        df.loc[:,"initial"] = df["initial"].cumprod()
        rst[acc.name]["最新净值"] = "{:.3f}".format(df.ix[-1]["account"]/df.ix[-1,"initial"])
        rst[acc.name]["年化收益"] = (df.ix[-1]["account"]/df.ix[-1,"initial"]-1)*100/df.shape[0]*250
        rst[acc.name]["年化波动率"] = 100*((df["account"]/df["initial"]).shift(-1)/(df["account"]/df["initial"])-1).fillna(0).std()*math.sqrt(250)
        rst[acc.name]["夏普率"] = "{:.2f}".format(rst[acc.name]["年化收益"]/rst[acc.name]["年化波动率"])
        rst[acc.name]["年化收益"] = "{:.2f}%".format(rst[acc.name]["年化收益"])
        try:
            rst[acc.name]["今日收益"] = "{:.3f}%".format(100*(df.ix[-1]["account"]/df.ix[-1,"initial"])/(df.ix[-2]["account"]/df.ix[-2,"initial"])-100)
        except:pass
    df_all = pd.DataFrame(temp_all)
    df_all.ix[0,"initial"] = df_all.ix[0,"account"]
    df_all.fillna(0,inplace=True)
    filt = df_all["initial"]==0
    df_all.loc[filt,"initial"] = 1+df_all.loc[filt,"change"]/(df_all.loc[filt,"account"]-df_all.loc[filt,"change"]) 
    df_all.loc[:,"initial"] = df_all["initial"].cumprod()
    values = df["account"]/df["initial"]
        
    return render(request, 'index.html',{"data":rst,
                                         "x":[i.strftime('%Y-%m-%d') for i in values.index],
                                         "y":[i for i in values.values],
                                         "ymin":values.min(),
                                         "ymax":values.max(),
                                         "name":project})

def holdlist(request,account):
    acc = Account.objects.get(account=account)
    futuredata = []
    stockdata = []
    if acc.type in ["股票","固收"]:
        stockdata = [{"code":i.code,
                      "name":i.name,
                      "market_value":i.market_value,
                      "number":i.number,
                      "profit_loss":i.profit_loss,
                      "color":(lambda x :True if x >=0 else False)(i.profit_loss),
                      "rate":"{:.2%}".format(i.market_value/acc.total_assets)} for i in StockHoldList.objects.filter(number__gt=0).all()]
        
    else:
        futuredata = [{"code":i.code,
                       "useMargin":i.useMargin,
                       "number":i.number,
                       "profit_loss":"{:.2f}".format(i.profit_loss),
                       "color":(lambda x :True if x >=0 else False)(i.profit_loss),
                       "rate":"{:.2%}".format(i.useMargin/acc.total_assets),
                       "direction": (lambda x :"买入" if x==2 else "卖出")(i.direction)}  \
                       for i in FuturesHoldList.objects.filter(number__gt=0).all() if "&" not in i.code
                      ]
    return render(request, 'holdlist.html',{"stockdata":stockdata,"futuredata":futuredata})

# class holdlist(generics.GenericAPIView):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
# #     permission_classes = (permissions.IsAdminUser,)
#      
#     queryset = Account.objects.all()
#     serializer_class = IndexSerializer
#     
#     def get(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         data = {}
#         for a in serializer.data:
#             project = a["project"]
# #             name = a["name"]
#             if not data.__contains__(project):
#                 data[project] = {"股票":[],
#                                  "期货":[]}
#             
#             if a["type"] == "股票":
#                 for item in a["holdlist"]:
#                     d = {}
#                     d["code"] = item.code
#                     d["name"] = item.name
#                     d["value"] = item.market_value
#                     d["number"] = item.number
#                     d["profit_loss"] = "{:.2f}".format(item.profit_loss)
#                     data[project]["股票"].append(d)
#             else:
#                 for item in a["holdlist"]:
#                     if "&" in item.code:continue
#                     d = {}
#                     d["name"] = item.code
#                     d["useMargin"] =  item.useMargin
#                     d["number"] = item.number
#                     d["profit_loss"] = "{:.2f}".format(item.profit_loss)
#                     d["rate"] = "{:.2%}".format(d["useMargin"]/a["accountinfo"].total_assets)
#                     d["direction"] = (lambda x :"买入" if x==2 else "卖出")(item.direction)
#                     data[project]["期货"].append(d)
#         return render(request, 'holdlist.html',{"data":data})

# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import api_view, permission_classes
# @api_view(['GET'])
# @permission_classes((IsAuthenticated, ))
def index(request):
    rst = collections.OrderedDict()
    temp = {}
    accounts = Account.objects.all()
    fields = ["产品名字","总资产","净值","总盈亏率","总盈亏","股票盈亏","股票持仓",
              "对冲盈亏","对冲持仓","期货盈亏","期货持仓","固收盈亏","股票敞口",
              "期货敞口","股票多头占比","期货风险度","期货杠杆"]
    ckfunc = lambda x,y: (x-y)/(x+y) if x+y >0 else 0
    fxdfunc = lambda x,y,z: z/(x+y) if x+y >0 else 0
    ggfunc = lambda x,y,z: (x+y)/z if z >0 else 0
    gpckfunc = lambda x,y,z:(x-y+z)/(x+y-z) if (x+y-z)>0 else 0
    gpdtzbfunc = lambda x,y,z: z/(x+y) if x+y >0 else 0
    for acc in accounts:
        changehistory = Moneyhistory.objects.filter(account=acc).all()
        
        project = acc.project.name
        money = acc.total_assets
        rest = acc.rest_capital
        market_value = acc.market_value
        earnest = acc.earnest_capital
        
        initial = 0
        for i in changehistory:
            initial += i.money
        
        if rst.__contains__(project):
            rst[project]["总资产"]["value"] += money
        else:
            rst[project] = collections.OrderedDict()
            temp[project] = {}
            for k in fields:
                rst[project][k] = {"value":0,"link":""}
            temp[project]["stock"] = {}
            temp[project]["future"] = {}
            temp[project]["change"] = {}
            temp[project]["对冲空头"] = 0
            temp[project]["对冲多头"] = 0
            temp[project]["期货多头"] = 0
            temp[project]["期货空头"] = 0
            temp[project]["期货总资金"] = 0
            temp[project]["固收总资金"] = 0
            temp[project]["对冲总资金"] = 0
            temp[project]["股票总资金"] = 0
            rst[project]["产品名字"]["value"] = project
            rst[project]["总资产"]["value"] = money
            rst[project]["净值"]["value"] = 1
            
            
        if acc.type == "股票":
            rst[project]["股票盈亏"]["value"] += money - initial
            rst[project]["股票持仓"]["value"] += market_value
            temp[project]["股票总资金"] += money 
        elif acc.type == "期货":
            rst[project]["期货盈亏"]["value"] += money - initial
            rst[project]["期货持仓"]["value"] += earnest
            temp[project]["期货总资金"] += money
            holdlists = FuturesHoldList.objects.filter(account=acc).all()
            for i in holdlists:
                if i.direction == 2:
                    temp[project]["期货多头"] += i.lastprice*i.volumemultiple*i.number
                else :
                    temp[project]["期货空头"] += i.lastprice*i.volumemultiple*i.number
        elif acc.type == "对冲":
            rst[project]["对冲盈亏"]["value"] += money - initial
            rst[project]["对冲持仓"]["value"] += earnest
            temp[project]["对冲总资金"] += money
            if i.direction == 2:
                temp[project]["期货多头"] += i.lastprice*i.volumemultiple*i.number
            else :
                temp[project]["期货空头"] += i.lastprice*i.volumemultiple*i.number
            
        else:
            rst[project]["固收盈亏"]["value"] += money - initial
            temp[project]["固收总资金"] += money
        
        rst[project]["总盈亏"]["value"] += money - initial
        
        stockhistory = StockHistory.objects.filter(account=acc).all()
        futurehistory = FuturesHistory.objects.filter(account=acc).all()
        for i in stockhistory:
            if temp[project]["stock"].__contains__(i.date):
                temp[project]["stock"][i.date] += i.total_assets
            else:
                temp[project]["stock"][i.date] = i.total_assets
        for i in futurehistory:
            if temp[project]["future"].__contains__(i.date):
                temp[project]["future"][i.date] += i.total_assets
            else:
                temp[project]["future"][i.date] = i.total_assets
        for i in changehistory:
            if temp[project]["change"].__contains__(i.date):
                temp[project]["change"][i.date] += i.money
            else:
                temp[project]["change"][i.date] = i.money
            
    for project in temp.keys():
        df = pd.DataFrame({"stock":temp[project]["stock"],
                           "future":temp[project]["future"],
                           "change":temp[project]["change"]})
        df.ix[0,"initial"] = df.ix[0][["stock","future"]].sum()
        df.fillna(0,inplace=True)
        df.loc[df["initial"]==0,"initial"] = 1+ df.loc[df["initial"]==0,"change"]/(df[df["initial"]==0][["stock","future"]].sum(axis=1)-df.loc[df["initial"]==0,"change"]) 
        df.loc[:,"initial"] = df["initial"].cumprod()
        rst[project]["净值"]["value"] = df.ix[-1][["stock","future"]].sum()/df.ix[-1,"initial"]
        rst[project]["股票敞口"]["value"] = gpckfunc(rst[project]["股票持仓"]["value"],temp[project]["对冲多头"],temp[project]["对冲空头"])
        rst[project]["期货敞口"]["value"] = ckfunc(temp[project]["期货多头"],temp[project]["期货空头"])
        rst[project]["股票多头占比"]["value"] = gpdtzbfunc(temp[project]["股票总资金"],temp[project]["对冲总资金"],rst[project]["股票持仓"]["value"])
        rst[project]["期货风险度"]["value"] = fxdfunc(temp[project]["固收总资金"],temp[project]["期货总资金"],rst[project]["期货持仓"]['value'])
        rst[project]["期货杠杆"]["value"] = ggfunc(temp[project]["期货多头"],temp[project]["期货空头"],temp[project]["期货总资金"])
        rst[project]["产品名字"]["link"] = "/product/{}".format(project)
        rst[project]["总盈亏率"]["value"] = rst[project]["总盈亏"]["value"]/rst[project]["总资产"]["value"]
        for i in fields[1:]:
            rst[project][i]["value"] = ("%.3f" % rst[project][i]["value"]) 
    return render(request, 'product.html',{"data":rst,"fd":fields})

def value(request,account):
    temp = {}
    acc = Account.objects.get(name=account)
    temp["change"] = {i.date:i.money for i in Moneyhistory.objects.filter(account=acc)}
    
    if acc.type in ["股票","固收"]:
        temp["account"] = {i.date:i.total_assets for i in StockHistory.objects.filter(account=acc)}
    else:
        temp["account"] = {i.date:i.total_assets for i in FuturesHistory.objects.filter(account=acc)}
    
    df = pd.DataFrame(temp)
    df.ix[0,"initial"] = df.ix[0,"account"]
    df.fillna(0,inplace=True)
    filt = df["initial"]==0
    df.loc[df["initial"]==0,"initial"] = 1+df.loc[filt,"change"]/(df.loc[filt,"account"]-df.loc[filt,"change"]) 
    df.loc[:,"initial"] = df["initial"].cumprod()
    
    values = df["account"]/df["initial"]
        
    return render(request, 'value.html',{"x":[i.strftime('%Y-%m-%d') for i in values.index],
                                         "y":[i for i in values.values],
                                         "ymin":values.min(),
                                         "ymax":values.max(),
                                         "name":account})




# class product1(generics.GenericAPIView):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
# #     permission_classes = (permissions.IsAdminUser,)
#      
#     queryset = Account.objects.all()
#     serializer_class = IndexSerializer
#     
#     def get(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         fileds = ["account_num","value","year_profit","day_profit","mon_profit",
#                   "total_profit","year_profit_money","mon_profit_money","total_profit_money","day_profit_money"]
#         
#         data = {"total":{k:0 for k in fileds},
#                 "stock":{k:0 for k in fileds},
#                 "future":{k:0 for k in fileds},
#                 "products":[]}
#         
#         for a in serializer.data:
#             if a["accountinfo"].total_assets <=0:continue
#             
#             data["total"]["account_num"] += 1
#             data["total"]["value"] += a["accountinfo"].total_assets
#             data["total"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
#             data["total"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
#             data["total"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
#             data["total"]["day_profit_money"] += a["accountinfo"].total_assets-a["yesterdayinfo"].total_assets
#              
#             if a["type"] == "股票":
#                 data["stock"]["account_num"] += 1
#                 data["stock"]["value"] += a["accountinfo"].total_assets
#                 data["stock"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
#                 data["stock"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
#                 data["stock"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
#                 a["holdrate"] = "{:.2f}%".format(100*a["accountinfo"].market_value/a["accountinfo"].total_assets)
#           
#             else:
#                 data["future"]["account_num"] += 1
#                 data["future"]["value"] += a["accountinfo"].total_assets
#                 data["future"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
#                 data["future"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
#                 data["future"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
#                 a["holdrate"] = "{:.2f}%".format(100*a["accountinfo"].earnest_capital/a["accountinfo"].total_assets)
#             
#             a["history_profit"] = "{:.2f}%".format(100*(a["accountinfo"].total_assets/a["initial_capital"]-1))
#             a["day_profit"] = "{:.2f}%".format(100*(a["accountinfo"].total_assets-a["yesterdayinfo"].total_assets)/a["yesterdayinfo"].total_assets)
#             a["holdnum"] =len(a["holdlist"])
#             data["products"].append(a)
#              
#         data["total"]["year_profit"] = "{:.2f}%".format(self.divid(data["total"]["year_profit_money"],data["total"]["value"]))
#         data["total"]["mon_profit"] = "{:.2f}%".format(self.divid(data["total"]["mon_profit_money"],data["total"]["value"]))
#         data["total"]["total_profit"] = "{:.2f}%".format(self.divid(data["total"]["total_profit_money"],data["total"]["value"]))
#         data["total"]["day_profit"] = "{:.2f}%".format(self.divid(data["total"]["day_profit_money"],data["total"]["value"]))
#          
#         data["stock"]["year_profit"] = "{:.2f}%".format(self.divid(data["stock"]["year_profit_money"],data["total"]["value"]))
#         data["stock"]["mon_profit"] = "{:.2f}%".format(self.divid(data["stock"]["mon_profit_money"],data["total"]["value"]))
#         data["stock"]["total_profit"] = "{:.2f}%".format(self.divid(data["stock"]["total_profit_money"],data["total"]["value"]))
#         
#         data["future"]["year_profit"] = "{:.2f}%".format(self.divid(data["future"]["year_profit_money"],data["total"]["value"]))
#         data["future"]["mon_profit"] = "{:.2f}%".format(self.divid(data["future"]["mon_profit_money"],data["total"]["value"]))
#         data["future"]["total_profit"] = "{:.2f}%".format(self.divid(data["future"]["total_profit_money"],data["total"]["value"]))
#         return render(request, 'index.html',{"data":data})
# 
#     def divid(self,a,b):
#         if b-a <=0:return 0
#         return 100*a/(b-a)
#             
#     def updateproduct(self,data,newdata):
#         if data["date"] < newdata["create_time"]:
#             data["date"]=newdata["create_time"]
#         data["number"] += len(newdata["holdlist"])
#         data["marketvalue"] += newdata["market_value"]
