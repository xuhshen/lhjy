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
from _ast import Lambda

class index(generics.GenericAPIView):
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
            data["total"]["day_profit_money"] += a["accountinfo"].profit_loss
             
            if a["type"] == "股票":
                data["stock"]["account_num"] += 1
                data["stock"]["value"] += a["accountinfo"].total_assets
                data["stock"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
                data["stock"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
                data["stock"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
                a["holdrate"] = "{:.2f}%".format(self.divid(a["accountinfo"].market_value,a["accountinfo"].total_assets)*100)
          
            else:
                data["future"]["account_num"] += 1
                data["future"]["value"] += a["accountinfo"].total_assets
                data["future"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
                data["future"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
                data["future"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
                a["holdrate"] = "{:.2f}%".format(100*a["accountinfo"].earnest_capital/a["accountinfo"].total_assets)
            
            a["history_profit"] = "{:.2f}%".format(100*(a["accountinfo"].total_assets/a["initial_capital"]-1))
            a["day_profit"] = "{:.2f}%".format(self.divid(a["accountinfo"].profit_loss,a["accountinfo"].total_assets))
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
                    d = {}
                    d["name"] = item.code
                    d["useMargin"] =  item.useMargin
                    d["number"] = item.number
                    d["profit_loss"] = "{:.2f}".format(item.profit_loss)
                    d["rate"] = "{:.2%}".format(d["useMargin"]/a["accountinfo"].total_assets*100)
                    d["direction"] = (lambda x :"买入" if x==2 else "卖出")(item.direction)
                    data[project]["期货"].append(d)
#         
#     
        return render(request, 'holdlist.html',{"data":data})


def product(request):
    return render(request, 'product.html')

# def holdlist(request):
#     
#     return render(request, 'holdlist.html')


