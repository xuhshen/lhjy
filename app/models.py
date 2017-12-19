from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from pydoc import describe

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Action(models.Model):
    '''交易动作：买入，卖出, 买平，卖平，买开，卖开
    '''
    name = models.CharField(max_length=200,help_text="交易方向")
    def __str__(self):
        return self.name
    
class Status(models.Model):    
    '''交易状态：挂单，撤单，成交，部分成交
    '''
    status = models.CharField(max_length=200,help_text="交易状态")    
    def __str__(self):
        return self.status

class Company(models.Model):
    '''资金账户对应的券商，期货公司
    '''
    name = models.CharField(max_length=200,help_text="资金账户对应公司")
    def __str__(self):
        return self.name

class CategoryStatus(models.Model):
    '''定义交易品种的状态，比如股票是否停盘，
    '''
    name = models.CharField(max_length=50,help_text="交易品种状态")
    def __str__(self):
        return self.name
    
class Category(models.Model):
    '''交易品种，比如股票名，
    '''
    name = models.CharField(max_length=200,help_text="交易品种名字")
    code = models.CharField(max_length=50,help_text="交易品种代码")
    current_price = models.FloatField(default=0,help_text="交易品种当前价")
    status = models.ForeignKey(CategoryStatus, on_delete=models.CASCADE,help_text="交易品种状态") 
    
    def __str__(self):
        return self.name


class HoldCategory(models.Model):
    '''持仓的品种信息，持仓账户子信息
    '''
    code = models.ForeignKey(Category, on_delete=models.CASCADE,help_text="持仓品种代码")
    hold_number = models.FloatField(default=0,help_text="持仓数量")
    frozen_number = models.FloatField(default=0,help_text="冻结数量")
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code.name
    
    def get_marketvalue(self):
        market_value = self.hold_number * self.code.current_price
        return market_value

class AccountType(models.Model):
    value = models.CharField(max_length=100,help_text="资金账户类型定义")
    def __str__(self):
        return self.value

    
class CapitalAccount(models.Model):
    '''基金账户：账户名，账户密码，总资金，可用资金，市值
    '''
    company = models.ForeignKey(Company, on_delete=models.CASCADE,default=1,help_text="证券公司或者期货公司") 
    type = models.ForeignKey(AccountType, on_delete=models.CASCADE,default=1,help_text="账户类型，股票账户，期货账户，回测账户")
    
    product = models.CharField(max_length=200,help_text="产品名字")
    account_name = models.CharField(max_length=200,help_text="资金账号")
    account_pass = models.CharField(max_length=200,help_text="资金账号密码")
    
    total_money = models.FloatField(default=0,help_text="账户总资金")
    allocation_money = models.FloatField(default=0,help_text="可分配资金") #可分配资金
    enable_money = models.FloatField(default=0,help_text="可用资金") #可用资金
    ssag = models.CharField(max_length=200,help_text="上证股东代码") #上证股东代码
    szag = models.CharField(max_length=200,help_text="深证股东代码") #深证股东代码
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.product
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE,help_text="策略账户，也就是系统账户")
    capitalaccount = models.ForeignKey(CapitalAccount, on_delete=models.CASCADE,help_text="资金账户")
    
    total_money = models.FloatField(default=0,help_text="策略账户总资金")
    enable_money = models.FloatField(default=0,help_text="策略账户可用资金")
    
    holdlist = models.ManyToManyField(HoldCategory,blank=True,help_text="策略账户总持仓")
    
    create_time = models.DateTimeField(auto_now_add=True,help_text="创建时间")
    lastupdate_time = models.DateTimeField(auto_now=True,help_text="最后修改时间")
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
    strategy_account = models.ForeignKey(StrategyUser, on_delete=models.CASCADE,help_text="策略账户")
    trade_action = models.ForeignKey(Action, on_delete=models.CASCADE,default=1,help_text="交易方向")
    trade_category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1,help_text="交易对象")
    trade_status = models.ForeignKey(Status, on_delete=models.CASCADE,default=1,help_text="交易状态")
    
    ticket = models.CharField(max_length=200,help_text="证券公司的委托单号")
    
    price = models.FloatField(default=0,help_text="交易价格")
    pretrade_money = models.FloatField(default=0,help_text="预交易资金")
    pretrade_number = models.FloatField(default=0,help_text="预交易数量")
    is_market_price = models.BooleanField(default=False,help_text="是否市场价成交")
    
    already_trade_money = models.FloatField(default=0,help_text="实际已成交资金")
    already_trade_number = models.FloatField(default=0,help_text="实际已成交数量")
    
    waiting_trade_money = models.FloatField(default=0,help_text="等待成交金额")
    waiting_trade_number = models.FloatField(default=0,help_text="等待成交数量")
    
    create_time = models.DateTimeField(auto_now_add=True,help_text="请求创建时间")
    lastupdate_time = models.DateTimeField(auto_now=True,help_text="最后更新时间")
     
    def __str__(self):
        return self.trade_category.code





        