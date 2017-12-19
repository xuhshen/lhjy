from django.contrib.auth.models import User, Group
from rest_framework import serializers
from app.models import *
from rest_framework.exceptions import ErrorDetail, ValidationError

class IndexSerializer(serializers.ModelSerializer):
    pass 