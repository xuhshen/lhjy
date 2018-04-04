from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
import datetime

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

class Company(models.Model):
    '''资金账户对应的券商，期货公司
    '''
    name = models.CharField(max_length=200,help_text="资金账户对应公司")
    def __str__(self):
        return self.name
    
class Project(models.Model):
    '''项目名字
    '''
    name = models.CharField(max_length=200,help_text="项目名字")
    def __str__(self):
        return self.name
    
class Account(models.Model):
    name = models.CharField(max_length=100,help_text="账户名")
    account = models.CharField(max_length=50,help_text="账户号")
    type = models.CharField(max_length=50,default="股票",help_text="账户类型")
    company = models.ForeignKey(Company, on_delete=models.CASCADE,help_text="券商") 
    project = models.ForeignKey(Project, on_delete=models.CASCADE,help_text="项目") 
    initial_capital = models.FloatField(default=0,help_text="初始资金")
    
    rest_capital = models.FloatField(default=0,help_text="资金余额")
    total_assets = models.FloatField(default=0,help_text="总资产")
    market_value = models.FloatField(default=0,help_text="最新市值")
    earnest_capital = models.FloatField(default=0,help_text="保证金")
    
    starttime = models.DateTimeField(blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "{}({})".format(self.account,self.name)
    
    def getholdlist(self):
        
        if self.type == "股票":
            rst = StockHoldList.objects.filter(account=self,number__gt=0)
        else:
            rst = FuturesHoldList.objects.filter(account=self,number__gt=0)
        return rst
        
        return rst
    
    def getholdnum(self):
        return len(self.getholdlist())
    
    def getlatestinfo(self):
        if self.type == "股票":
            rst = StockHistory.objects.filter(account=self).order_by("-date")[0]
        else:
            rst = FuturesHistory.objects.filter(account=self).order_by("-date")[0]
        return rst
    
    
    def getyesterdayinfo(self):
        try:
            if self.type == "股票":
                rst = StockHistory.objects.filter(account=self).order_by("-date")[1]
            else:
                rst = FuturesHistory.objects.filter(account=self).order_by("-date")[1]
        except:
            rst = {}
        return rst
    
    def getyearstartinfo(self):
        y = datetime.datetime.now().year-1
        y_date = datetime.datetime.strptime("{}-12-28".format(y),'%Y-%m-%d')
        if self.type == "股票":
            rst = StockHistory.objects.filter(account=self,date__gt=y_date).order_by("date")[0]
        else:
            rst = FuturesHistory.objects.filter(account=self,date__gt=y_date).order_by("date")[0]
        return rst
    
    def getmonstartinfo(self):
        m_date = datetime.datetime.now()-datetime.timedelta(days=30)
        if self.type == "股票":
            rst = StockHistory.objects.filter(account=self,date__gt=m_date).order_by("date")[0]
        else:
            rst = FuturesHistory.objects.filter(account=self,date__gt=m_date).order_by("date")[0]
        return rst
    
    def getlastinfo(self):
        if self.type == "股票":
            rst = StockHistory.objects.filter(account=self).order_by("date")[0]
        else:
            rst = FuturesHistory.objects.filter(account=self).order_by("date")[0]
        return rst

class Moneyhistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
    date = models.DateField()
    money = models.FloatField(default=0,help_text="资金进出")
    description = models.TextField(default="",blank=True,help_text="资金进出说明")
    
    def __str__(self):
        return self.account.name 

#     def get_holdlist(self):
#         holdlist = []
#         for strategy_user in StrategyUser.objects.filter(capitalaccount=self):
#             holdlist.append(strategy_user.holdlist.all())
#         return holdlist

# class StockLatestRecord(models.Model):
#     '''存放账户最新的状态数据
#     '''
#     account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
#     rest_capital = models.FloatField(default=0,help_text="资金余额")
#     enable_capital = models.FloatField(default=0,help_text="可用资金")
#     frozen_capital = models.FloatField(default=0,help_text="冻结资金")
#     market_value = models.FloatField(default=0,help_text="最新市值")
#     total_assets = models.FloatField(default=0,help_text="总资产")
#     profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
#     preferred_capital = models.FloatField(default=0,help_text="可取资金")
#     margin_selling_capital = models.FloatField(default=0,help_text="融券卖出资金")
#     counters_bought_number = models.FloatField(default=0,help_text="取柜台可买数量")
#     create_time = models.DateTimeField(auto_now_add=True)
#     lastupdate_time = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return self.account.name

class StockHistory(models.Model):
    '''存放账户历史结算信息
    '''
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
    date = models.DateField()
    rest_capital = models.FloatField(default=0,help_text="资金余额")
    enable_capital = models.FloatField(default=0,help_text="可用资金")
    frozen_capital = models.FloatField(default=0,help_text="冻结资金")
    market_value = models.FloatField(default=0,help_text="最新市值")
    total_assets = models.FloatField(default=0,help_text="总资产")
    profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
    preferred_capital = models.FloatField(default=0,help_text="可取资金")
    margin_selling_capital = models.FloatField(default=0,help_text="融券卖出资金")
    counters_bought_number = models.FloatField(default=0,help_text="取柜台可买数量")
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.account.name

class StockTicket(models.Model):
    '''存放股票历史委托单信息
    '''
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
    order_date = models.CharField(max_length=200,help_text="委托日期")
    order_time = models.CharField(max_length=200,help_text="委托时间") 
    code = models.CharField(max_length=30,help_text="证券代码")
    name = models.CharField(max_length=30,help_text="证券名称")
    action = models.CharField(max_length=30,help_text="买卖标志")
    order_price = models.FloatField(default=0,help_text="委托价格")
    order_number = models.FloatField(default=0,help_text="委托数量")
    order_ticket = models.CharField(max_length=30,help_text="委托编号")
    deal_number = models.FloatField(default=0,help_text="成交数量")
    deal_money = models.FloatField(default=0,help_text="成交金额")
    cancel_number = models.FloatField(default=0,help_text="撤单数量")
    cancel_mark = models.CharField(max_length=30,help_text="撤单标志")
    
    def __str__(self):
        return "{} {}({})".format(self.order_time,self.order_ticket,self.code)

class StockHoldList(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户")
    code = models.CharField(max_length=30,help_text="证券代码")
    name = models.CharField(max_length=30,help_text="证券名称")
    number = models.FloatField(default=0,help_text="证券数量")
    enable_number = models.FloatField(default=0,help_text="可卖数量")
    buy_price = models.FloatField(default=0,help_text="成本价")
    cost = models.FloatField(default=0,help_text="盈亏成本价")
    current_price = models.FloatField(default=0,help_text="当前价")
    market_value = models.FloatField(default=0,help_text="最新市值")
    profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
    profit_loss_rate = models.FloatField(default=0,help_text="盈亏比例")
    buy_financing_balance = models.FloatField(default=0,help_text="融资买入证券实时余额")
    rest_buy_financing = models.FloatField(default=0,help_text="融资买入余额")
    enable_buy_financing = models.FloatField(default=0,help_text="融资买入可用")
    value_rate = models.FloatField(default=0,help_text="个股资产比例")
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "{}({})".format(self.code,self.account.name)
    

# class FuturesLatestRecord(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
#     date = models.DateField()
#     rest_capital = models.FloatField(default=0,help_text="资金余额")
#     total_assets = models.FloatField(default=0,help_text="总资产")
#     profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
#     earnest_capital = models.FloatField(default=0,help_text="保证金")
#     create_time = models.DateTimeField(auto_now_add=True)
#     lastupdate_time = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return self.account.name

class FuturesHistory(models.Model):
    '''存放期货历史数据信息
    '''
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
    date = models.DateField()
    rest_capital = models.FloatField(default=0,help_text="资金余额")
    total_assets = models.FloatField(default=0,help_text="总资产")
    profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
    earnest_capital = models.FloatField(default=0,help_text="保证金")
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.account.name
    

class FuturesHoldList(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE,help_text="交易账户") 
    code = models.CharField(max_length=30,help_text="合约代码")
    number = models.FloatField(default=0,help_text="持仓数量")
    rate = models.FloatField(default=0,help_text="保证金率")
    useMargin = models.FloatField(default=0,help_text="占用保证金")
    cost = models.FloatField(default=0,help_text="持仓成本")
    direction = models.FloatField(default=0,help_text="交易方向(2:买入 3:卖出)")
    profit_loss = models.FloatField(default=0,help_text="浮动盈亏")
    lastprice = models.FloatField(default=0,help_text="最新价格")
    volumemultiple = models.FloatField(default=0,help_text="合约乘数")
    
    create_time = models.DateTimeField(auto_now_add=True)
    lastupdate_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.code
































##################################################################################


#     
# class Status(models.Model):    
#     '''交易状态：挂单，撤单，成交，部分成交
#     '''
#     status = models.CharField(max_length=200,help_text="交易状态")    
#     def __str__(self):
#         return self.status
# 
# class CategoryStatus(models.Model):
#     '''定义交易品种的状态，比如股票是否停盘，
#     '''
#     name = models.CharField(max_length=50,help_text="交易品种状态")
#     def __str__(self):
#         return self.name
#     
# class Category(models.Model):
#     '''交易品种，比如股票名，
#     '''
#     name = models.CharField(max_length=200,help_text="交易品种名字")
#     code = models.CharField(max_length=50,help_text="交易品种代码")
#     current_price = models.FloatField(default=0,help_text="交易品种当前价")
#     status = models.ForeignKey(CategoryStatus, on_delete=models.CASCADE,help_text="交易品种状态") 
#     
#     def __str__(self):
#         return self.name
# 
# 
# class HoldCategory(models.Model):
#     '''持仓的品种信息，持仓账户子信息
#     '''
#     code = models.ForeignKey(Category, on_delete=models.CASCADE,help_text="持仓品种代码")
#     hold_number = models.FloatField(default=0,help_text="持仓数量")
#     frozen_number = models.FloatField(default=0,help_text="冻结数量")
#     
#     create_time = models.DateTimeField(auto_now_add=True)
#     lastupdate_time = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return self.code.name
#     
#     def get_marketvalue(self):
#         market_value = self.hold_number * self.code.current_price
#         return market_value
# 
# class AccountType(models.Model):
#     name = models.CharField(max_length=100,help_text="资金账户类型定义")
#     def __str__(self):
#         return self.name
# 
#     
# class CapitalAccount(models.Model):
#     '''基金账户：账户名，账户密码，总资金，可用资金，市值
#     '''
#     company = models.ForeignKey(Company, on_delete=models.CASCADE,default=1,help_text="证券公司或者期货公司") 
#     type = models.ForeignKey(AccountType, on_delete=models.CASCADE,default=1,help_text="账户类型，股票账户，期货账户，回测账户")
#     
#     product = models.CharField(max_length=200,help_text="产品名字")
#     account_name = models.CharField(max_length=200,help_text="资金账号")
#     account_pass = models.CharField(max_length=200,help_text="资金账号密码")
#     
#     initial_money = models.FloatField(default=0,help_text="账户初始资金")
#     total_money = models.FloatField(default=0,help_text="账户总资金")
#     allocation_money = models.FloatField(default=0,help_text="可分配资金") #可分配资金
#     enable_money = models.FloatField(default=0,help_text="可用资金") #可用资金
#     ssag = models.CharField(max_length=200,blank=True,help_text="上证股东代码") #上证股东代码
#     szag = models.CharField(max_length=200,blank=True,help_text="深证股东代码") #深证股东代码
#     
#     create_time = models.DateTimeField(auto_now_add=True)
#     lastupdate_time = models.DateTimeField(auto_now=True)
#     today_profit = models.FloatField(default=0,help_text="当天收益") 
#     
#     def __str__(self):
#         return self.product
#     
#     def get_holdlist(self):
#         holdlist = []
#         for strategy_user in StrategyUser.objects.filter(capitalaccount=self):
#             holdlist.append(strategy_user.holdlist.all())
#         return holdlist
# 
#     def get_market_value(self):
#         market_value = 0
#         for strategy_user in StrategyUser.objects.filter(capitalaccount=self):
#             market_value += strategy_user.get_total_market_value()
#         return market_value
# 
# 
# class StrategyUser(models.Model):
#     '''策略账户：策略账户名，基金账户，总资金，可用资金
#     '''
#     user = models.ForeignKey(User, on_delete=models.CASCADE,help_text="策略账户，也就是系统账户")
#     capitalaccount = models.ForeignKey(CapitalAccount, on_delete=models.CASCADE,help_text="资金账户")
#     
#     total_money = models.FloatField(default=0,help_text="策略账户总资金")
#     enable_money = models.FloatField(default=0,help_text="策略账户可用资金")
#     
#     holdlist = models.ManyToManyField(HoldCategory,blank=True,help_text="策略账户总持仓")
#     
#     create_time = models.DateTimeField(auto_now_add=True,help_text="创建时间")
#     lastupdate_time = models.DateTimeField(auto_now=True,help_text="最后修改时间")
#     def __str__(self):
#         return self.user.username
#     
#     def get_total_market_value(self):
#         market_value = 0
#         for category in self.holdlist.all():
#             market_value += category.get_marketvalue()
#         
#         return market_value
# 
# class Record(models.Model):
#     '''每次委托的状态记录
#     '''
#     strategy_account = models.ForeignKey(StrategyUser, on_delete=models.CASCADE,help_text="策略账户")
#     trade_action = models.ForeignKey(Action, on_delete=models.CASCADE,default=1,help_text="交易方向")
#     trade_category = models.ForeignKey(Category, on_delete=models.CASCADE,default=1,help_text="交易对象")
#     trade_status = models.ForeignKey(Status, on_delete=models.CASCADE,default=1,help_text="交易状态")
#     
#     ticket = models.CharField(max_length=200,help_text="证券公司的委托单号")
#     
#     price = models.FloatField(default=0,help_text="交易价格")
#     pretrade_money = models.FloatField(default=0,help_text="预交易资金")
#     pretrade_number = models.FloatField(default=0,help_text="预交易数量")
#     is_market_price = models.BooleanField(default=False,help_text="是否市场价成交")
#     
#     already_trade_money = models.FloatField(default=0,help_text="实际已成交资金")
#     already_trade_number = models.FloatField(default=0,help_text="实际已成交数量")
#     
#     waiting_trade_money = models.FloatField(default=0,help_text="等待成交金额")
#     waiting_trade_number = models.FloatField(default=0,help_text="等待成交数量")
#     
#     create_time = models.DateTimeField(auto_now_add=True,help_text="请求创建时间")
#     lastupdate_time = models.DateTimeField(auto_now=True,help_text="最后更新时间")
#      
#     def __str__(self):
#         return self.trade_category.code





        