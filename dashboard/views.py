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
#         account = AccountType.objects.all()
#         data = {str(i.id):[i.name,0] for i in account}
#         data["product"] = {}
#         data["totalprofit"] = 0
#         data["dayprofit"] = 0
#         
#         for i in serializer.data:
#             if data["product"].__contains__(i["product"]):
#                 self.updateproduct(data["product"][i["product"]][i["account_name"]],i)
#             else:
#                 data["product"][i["product"]] = {i["account_name"]:i}
#                 
#             data[str(i["type"])][1] += 1
#             data["dayprofit"] += round(i["today_profit"],2)
#             data["totalprofit"] += round(i["total_money"]/(i["initial_money"]+0.0000001)-1,2)
        data={
               "total":{"account_num":2,
                        "value":2000000,
                        "year_profit":0,
                        "day_profit":0,
                        "mon_profit":0,
                        "total_profit":0
                        },
               "stock":{"account_num":2,
                        "value":1000000,
                        "year_profit_money":100000,
                        "year_profit":"10%",
                        "day_profit":"10%",
                        "mon_profit":"10%",
                        "total_profit":"10%"},
               "future":{"account_num":2,
                         "value":1000000,
                         "year_profit_money":100000,
                         "year_profit":"10%",
                        "day_profit":"10%",
                        "mon_profit":"10%",
                        "total_profit":"10%"},
              "products":[
                    {
                     "name":"基金一号",
                     "stime":"2017-11-11",
                     "holdbum":"10",
                     "holdrate":"10%",
                     "day_profit":"0.1%",
                     "history_profit":"10%",
                     "type":"股票"},
                          {
                     "name":"基金二号",
                     "stime":"2017-11-11",
                     "holdbum":"10",
                     "holdrate":"10%",
                     "day_profit":"0.1%",
                     "history_profit":"10%",
                     "type":"股票"},
                          {
                     "name":"基金san号",
                     "stime":"2017-11-11",
                     "holdbum":"10",
                     "holdrate":"10%",
                     "day_profit":"0.1%",
                     "history_profit":"10%",
                     "type":"期货"},
                  ]
              }    
        print (data)
        return render(request, 'index.html',{"data":data})

    def updateproduct(self,data,newdata):
        if data["date"] < newdata["create_time"]:
            data["date"]=newdata["create_time"]
        data["number"] += len(newdata["holdlist"])
        data["marketvalue"] += newdata["market_value"]

def product(request):
    return render(request, 'product.html')

def holdlist(request):
    return render(request, 'holdlist.html')


