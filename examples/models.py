import datetime

from django.db import models
from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from lib2to3.fixer_util import Number
from email.policy import default
from django.db.models.fields.related import ManyToManyField

class Action(models.Model):
    '''交易动作：买入，卖出
    '''
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name
    
class Status(models.Model):    
    '''交易状态：挂单，撤单，成交，部分成交
    '''
    status = models.CharField(max_length=200)    
    def __str__(self):
        return self.status

class Capitalaccount(models.Model):
    '''基金账户：账户名，账户密码，总资金，可用资金，市值
    '''
    account_name = models.CharField(max_length=200)
    account_pass = models.CharField(max_length=200)
    total_money = models.FloatField(default=0)
    enable_money = models.FloatField(default=0)
    market_value = models.FloatField(default=0)
    
    def __str__(self):
        return self.account_name

class Strategy_user(models.Model):
    '''策略账户：策略账户名，基金账户，总资金，可用资金
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    capitalaccount = models.ForeignKey(Capitalaccount, on_delete=models.CASCADE)
    total_money = models.FloatField(default=0)
    enable_money = models.FloatField(default=0)
    def __str__(self):
        return self.user.username
    
class Record(models.Model):
    '''交易记录：策略用户名，基金账户，状态，动作，代码，名字，数量，金额，成交金额，成交数量
    '''
    user = models.ForeignKey(Strategy_user, on_delete=models.CASCADE)
    account = models.ForeignKey(Capitalaccount, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200,blank=True)
    
    market_ticket = models.CharField(max_length=200,blank=True)
    
    number = models.FloatField()
    price = models.FloatField(blank=True)
    marker_price = models.BooleanField(default=False)
    
    trademoney = models.FloatField(default=0)
    tradenumber = models.FloatField(default=0)
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.user.username
    
    
class Dailyinfo(models.Model):  
    '''每天账户结算记录：策略用户名，基金账户
    '''
    user = models.ForeignKey(Strategy_user, on_delete=models.CASCADE) 
    account = models.ForeignKey(Capitalaccount, on_delete=models.CASCADE) 
    holdlist = models.TextField()
    money = models.FloatField()
    
    def __str__(self):
        return self.user.user.username
    
    
    
    
    
    
    
    

        
        
        