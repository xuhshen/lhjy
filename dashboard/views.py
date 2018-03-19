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

class product(generics.GenericAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
#     permission_classes = (permissions.IsAdminUser,)
     
    queryset = Account.objects.all()
    serializer_class = IndexSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        fileds = ["account_num","value","year_profit","day_profit","mon_profit",
                  "total_profit","year_profit_money","mon_profit_money","total_profit_money","day_profit_money"]
        
        data = {"total":{k:0 for k in fileds},
                "stock":{k:0 for k in fileds},
                "future":{k:0 for k in fileds},
                "products":[]}
        
        for a in serializer.data:
            if a["accountinfo"].total_assets <=0:continue
            
            data["total"]["account_num"] += 1
            data["total"]["value"] += a["accountinfo"].total_assets
            data["total"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
            data["total"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
            data["total"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
            data["total"]["day_profit_money"] += a["accountinfo"].total_assets-a["yesterdayinfo"].total_assets
             
            if a["type"] == "股票":
                data["stock"]["account_num"] += 1
                data["stock"]["value"] += a["accountinfo"].total_assets
                data["stock"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
                data["stock"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
                data["stock"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
                a["holdrate"] = "{:.2f}%".format(100*a["accountinfo"].market_value/a["accountinfo"].total_assets)
          
            else:
                data["future"]["account_num"] += 1
                data["future"]["value"] += a["accountinfo"].total_assets
                data["future"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
                data["future"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
                data["future"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
                a["holdrate"] = "{:.2f}%".format(100*a["accountinfo"].earnest_capital/a["accountinfo"].total_assets)
            
            a["history_profit"] = "{:.2f}%".format(100*(a["accountinfo"].total_assets/a["initial_capital"]-1))
            a["day_profit"] = "{:.2f}%".format(100*(a["accountinfo"].total_assets-a["yesterdayinfo"].total_assets)/a["yesterdayinfo"].total_assets)
            a["holdnum"] =len(a["holdlist"])
            data["products"].append(a)
             
        data["total"]["year_profit"] = "{:.2f}%".format(self.divid(data["total"]["year_profit_money"],data["total"]["value"]))
        data["total"]["mon_profit"] = "{:.2f}%".format(self.divid(data["total"]["mon_profit_money"],data["total"]["value"]))
        data["total"]["total_profit"] = "{:.2f}%".format(self.divid(data["total"]["total_profit_money"],data["total"]["value"]))
        data["total"]["day_profit"] = "{:.2f}%".format(self.divid(data["total"]["day_profit_money"],data["total"]["value"]))
         
        data["stock"]["year_profit"] = "{:.2f}%".format(self.divid(data["stock"]["year_profit_money"],data["total"]["value"]))
        data["stock"]["mon_profit"] = "{:.2f}%".format(self.divid(data["stock"]["mon_profit_money"],data["total"]["value"]))
        data["stock"]["total_profit"] = "{:.2f}%".format(self.divid(data["stock"]["total_profit_money"],data["total"]["value"]))
        
        data["future"]["year_profit"] = "{:.2f}%".format(self.divid(data["future"]["year_profit_money"],data["total"]["value"]))
        data["future"]["mon_profit"] = "{:.2f}%".format(self.divid(data["future"]["mon_profit_money"],data["total"]["value"]))
        data["future"]["total_profit"] = "{:.2f}%".format(self.divid(data["future"]["total_profit_money"],data["total"]["value"]))
        return render(request, 'index.html',{"data":data})

    def divid(self,a,b):
        if b-a <=0:return 0
        return 100*a/(b-a)
            
    def updateproduct(self,data,newdata):
        if data["date"] < newdata["create_time"]:
            data["date"]=newdata["create_time"]
        data["number"] += len(newdata["holdlist"])
        data["marketvalue"] += newdata["market_value"]



class holdlist(generics.GenericAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
#     permission_classes = (permissions.IsAdminUser,)
     
    queryset = Account.objects.all()
    serializer_class = IndexSerializer
    
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {}
        for a in serializer.data:
            project = a["project"]
#             name = a["name"]
            if not data.__contains__(project):
                data[project] = {"股票":[],
                                 "期货":[]}
            
            if a["type"] == "股票":
                for item in a["holdlist"]:
                    d = {}
                    d["code"] = item.code
                    d["name"] = item.name
                    d["value"] = item.market_value
                    d["number"] = item.number
                    d["profit_loss"] = "{:.2f}".format(item.profit_loss)
                    data[project]["股票"].append(d)
            else:
                for item in a["holdlist"]:
                    if "&" in item.code:continue
                    d = {}
                    d["name"] = item.code
                    d["useMargin"] =  item.useMargin
                    d["number"] = item.number
                    d["profit_loss"] = "{:.2f}".format(item.profit_loss)
                    d["rate"] = "{:.2%}".format(d["useMargin"]/a["accountinfo"].total_assets)
                    d["direction"] = (lambda x :"买入" if x==2 else "卖出")(item.direction)
                    data[project]["期货"].append(d)
#         
#     
        return render(request, 'holdlist.html',{"data":data})


def index(request):
    rst = collections.OrderedDict()
    accounts = Account.objects.all()
    for acc in accounts:
        changehistory = Moneyhistory.objects.filter(account=acc).all()
        
        project = acc.project.name
        money = acc.total_assets
        rest = acc.rest_capital
        earnest = acc.earnest_capital
        
        initial = acc.initial_capital
        for i in changehistory:
            initial += i.money
        
        if rst.__contains__(project):
            rst[project]["总资产"] += money
        else:
            rst[project] = collections.OrderedDict()
            rst[project]["stock"] = {}
            rst[project]["future"] = {}
            rst[project]["change"] = {}
            rst[project]["产品名字"] = project
            rst[project]["总资产"] = money
            rst[project]["净值"] = 1
            fields = ["总盈亏","股票盈亏","股票持仓","期货盈亏","期货持仓","固收盈亏"]
            for fd in fields:
                rst[project][fd] = 0
           
            
        if acc.type == "股票":
            rst[project]["股票盈亏"] += money - initial
            rst[project]["股票持仓"] += money - rest
        elif acc.type == "期货":
            rst[project]["期货盈亏"] += money - initial
            rst[project]["期货持仓"] += earnest
        elif acc.type == "对冲":
            rst[project]["对冲盈亏"] += money - initial
            rst[project]["对冲持仓"] += earnest
        else:
            rst[project]["固收盈亏"] += money - initial
        
        rst[project]["总盈亏"] += money - initial
        
        stockhistory = StockHistory.objects.filter(account=acc).all()
        futurehistory = FuturesHistory.objects.filter(account=acc).all()
        for i in stockhistory:
            if rst[project]["stock"].__contains__(i.date):
                rst[project]["stock"][i.date] += i.total_assets
            else:
                rst[project]["stock"][i.date] = i.total_assets
        for i in futurehistory:
            if rst[project]["future"].__contains__(i.date):
                rst[project]["future"][i.date] += i.total_assets
            else:
                rst[project]["future"][i.date] = i.total_assets
        for i in changehistory:
            if rst[project]["change"].__contains__(i.date):
                rst[project]["change"][i.date] += i.money
            else:
                rst[project]["change"][i.date] = i.money
            
    
    for project in rst.keys():
        df = pd.DataFrame({"stock":rst[project]["stock"],
                           "future":rst[project]["future"],
                           "change":rst[project]["change"]})
        df.ix[0,"initial"] = 1
        df.fillna(0,inplace=True)
        df.loc[df["initial"]==0,"initial"] = 1+ df.loc[df["initial"]==0,"change"]/df[df["initial"]==0][["stock","future"]].sum(axis=1) 
        df.loc[:,"initial"] = df["initial"].cumprod()
        rst[project]["净值"] = df.ix[-1][["stock","future"]].sum() /df.ix[-1,"initial"]
#         rst[project]["股票敞口"] = rst[project]["股票持仓"] - 
         
#     产品名、总资产、净值、总盈亏率、股票盈亏、对冲盈亏、期货盈亏、固收盈亏、股票敞口、期货敞口、股票多头占比、期货风险度、期货杠杆
    
    return render(request, 'product.html')

def value(request,account):
    acc = Account.objects.get(name=account)
    if acc.type == "股票":
        rst = StockHistory.objects.filter(account=acc)
    else:
        rst = FuturesHistory.objects.filter(account=acc)
    values = [[i.date,i.total_assets/acc.initial_capital] for i in rst]
    values = sorted(values, key=lambda x:(x[0] ))
    return render(request, 'value.html',{"x":[i[0].strftime('%Y-%m-%d') for i in values],
                                         "y":[i[1] for i in values],
                                         "ymin":min([i[1] for i in values]),
                                         "ymax":max([i[1] for i in values]),
                                         "name":account})



