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
                  "total_profit","year_profit_money","mon_profit_money","total_profit_money"]
        
        data = {"total":{k:0 for k in fileds},
                "stock":{k:0 for k in fileds},
                "future":{k:0 for k in fileds},
                "products":[]}
        
        for a in serializer.data:
            data["total"]["account_num"] += 1
            data["total"]["value"] += a["accountinfo"].total_assets
            data["total"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
            data["total"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
            data["total"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
            
            if a["type"] == "股票":
                data["stock"]["account_num"] += 1
                data["stock"]["value"] += a["accountinfo"].total_assets
                data["stock"]["year_profit_money"] += a["accountinfo"].total_assets-a["yearinfo"].total_assets
                data["stock"]["mon_profit_money"] += a["accountinfo"].total_assets-a["moninfo"].total_assets
                data["stock"]["total_profit_money"] += a["accountinfo"].total_assets-a["initial_capital"]
            else:
                pass
            
            a["holdrate"] = "{}%".format(self.divid(a["accountinfo"].market_value,a["accountinfo"].total_assets)*100)
            a["history_profit"] = "{}%".format(self.divid(a["accountinfo"].total_assets,a["initial_capital"])*100-100)
            
            a["day_profit"] = "{}%".format(self.divid(a["accountinfo"].total_assets,a["lastinfo"].total_assets)*100-100)
            
            data["products"].append(a)
            
            data["total"]["year_profit"] = self.divid(data["total"]["year_profit_money"],data["total"]["value"])
            data["total"]["mon_profit"] = self.divid(data["total"]["mon_profit_money"],data["total"]["value"])
            data["total"]["total_profit"] = self.divid(data["total"]["total_profit_money"],data["total"]["value"])
            
            data["stock"]["year_profit"] = self.divid(data["stock"]["year_profit_money"],data["total"]["value"])
            data["stock"]["mon_profit"] = self.divid(data["stock"]["mon_profit_money"],data["total"]["value"])
            data["stock"]["total_profit"] = self.divid(data["stock"]["total_profit_money"],data["total"]["value"])
            
        return render(request, 'index.html',{"data":data})

    def divid(self,a,b):
        b += 0.000001
        return a/b
            
    def updateproduct(self,data,newdata):
        if data["date"] < newdata["create_time"]:
            data["date"]=newdata["create_time"]
        data["number"] += len(newdata["holdlist"])
        data["marketvalue"] += newdata["market_value"]

def product(request):
    return render(request, 'product.html')

def holdlist(request):
    return render(request, 'holdlist.html')


