from django.contrib.auth.models import User, Group
from rest_framework import serializers
from app.models import *
from rest_framework.exceptions import ErrorDetail, ValidationError

class IndexSerializer(serializers.ModelSerializer):
#     holdlist = HoldCategory()
#     market_value = serializers.FloatField(source="get_market_value")
#     stockaccount = serializers.FloatField(source="get_market_value")
     
    class Meta:
        model = Account
        fields = "__all__" 