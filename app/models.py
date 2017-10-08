from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


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

class Company(models.Model):
    '''资金账户对应的券商，期货公司
    '''
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class CategoryStatus(models.Model):
    '''定义交易品种的状态，比如股票是否停盘，
    '''
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
class Category(models.Model):
    '''交易品种，比如股票名，
    '''
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    current_price = models.FloatField(default=0)
    status = models.ForeignKey(CategoryStatus, on_delete=models.CASCADE) 
    
    def __str__(self):
        return self.name


class HoldCategory(models.Model):
    '''持仓的品种信息，持仓账户子信息
    '''
    code = models.ForeignKey(Category, on_delete=models.CASCADE)
    hold_number = models.FloatField(default=0)
    frozen_number = models.FloatField(default=0)
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    
    def get_marketvalue(self):
        market_value = self.hold_number * self.code.current_price
        return market_value

class AccountType(models.Model):
    value = models.CharField(max_length=100)
    def __str__(self):
        return self.value
    
class CapitalAccount(models.Model):
    '''基金账户：账户名，账户密码，总资金，可用资金，市值
    '''
    company = models.ForeignKey(Company, on_delete=models.CASCADE,default=1) 
    type = models.ForeignKey(AccountType, on_delete=models.CASCADE,default=1)
    
    account_name = models.CharField(max_length=200)
    account_pass = models.CharField(max_length=200)
    
    total_money = models.FloatField(default=0)
    allocation_money = models.FloatField(default=0) #可分配资金
    enable_money = models.FloatField(default=0) #可用资金
    ssag = models.CharField(max_length=200) #上证股东代码
    szag = models.CharField(max_length=200) #深证股东代码
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.account_name
    
    def get_holdlist(self):
        holdlist = []
        for strategy_user in StrategyUser.objects.filter(capitalaccount=self):
            holdlist.append(strategy_user.holdlist.all())
        return holdlist

    def get_market_value(self):
        market_value = 0
        for strategy_user in StrategyUser.objects.filter(capitalaccount=self):
            market_value += strategy_user.get_total_market_value()
        return market_value
    
class StrategyUser(models.Model):
    '''策略账户：策略账户名，基金账户，总资金，可用资金
    '''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    capitalaccount = models.ForeignKey(CapitalAccount, on_delete=models.CASCADE)
    
    total_money = models.FloatField(default=0)
    enable_money = models.FloatField(default=0)
    
    holdlist = models.ManyToManyField(HoldCategory,blank=True)
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username
    
    def get_total_market_value(self):
        market_value = 0
        for category in self.holdlist.all():
            market_value += category.get_marketvalue()
        
        return market_value


class Record(models.Model):
    '''每次委托的状态记录
    '''
    strategy_account = models.ForeignKey(StrategyUser, on_delete=models.CASCADE)
    trade_action = models.ForeignKey(Action, on_delete=models.CASCADE,default=1)
    trade_category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1)
    trade_status = models.ForeignKey(Status, on_delete=models.CASCADE,default=1)
    
    ticket = models.CharField(max_length=200)
    
    price = models.FloatField(default=0)
    pretrade_money = models.FloatField(default=0)
    pretrade_number = models.FloatField(default=0)
    is_market_price = models.BooleanField(default=False)
    
    already_trade_money = models.FloatField(default=0)
    already_trade_number = models.FloatField(default=0)
    
    waiting_trade_money = models.FloatField(default=0)
    waiting_trade_number = models.FloatField(default=0)
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
     
    def __str__(self):
        return self.trade_category.code


        