# -*- coding: utf-8 -*-
import threading
import time
import datetime
import logging
import json
from StringIO import StringIO
# from _io import StringIO
from ctypes import *
import pandas as pd
import sys,os
#from imp import reload
print (sys.path)
basedir = os.path.dirname(sys.argv[0])
# dll = "trade_zx.dll"

sys.path.append("C:\\Users\\04yyl\\git\\lhjy\\deamo\\dlls")
print (sys.path)
class Pseudo_Dict(object):
    def __init__(self, _dict=None):
        if _dict:
            for _k, _v in _dict.items():
                self.__dict__[_k] = _v

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, key):
        return self.__dict__.get(key,None)

    def has_key(self, key):
        return self.__dict__.has_key(key)

    def get(self, key, value=None):
        return self.__dict__.get(key, value)

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return self.__dict__.get(key,None)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

# 全局变量
g = Pseudo_Dict({
    # 券商交易客户端登陆信息
    "host": "115.238.56.183",  # 券商交易服务器ip
    "port": 7708,  # 券商交易服务器Port
    "version": "8.19",  # tradex.dll 版本
    "yybid": 1,  # 券商营业部id
    "account_no": "******",  # 券商客户号
    "trade_account_no": "******",  #  券商资金帐户号
    "password": "****",  # 交易密码
    "tx_password": "",  # 通讯密码
})


'''
    接口简单封装/兼必要的数据缓存
'''


def _logon():
    '''
        试图登陆
    :return: client_id, err
    '''

    client_id = g.client_id
    if client_id is None:
        g.logger.info(u"试图登入交易服务器...")      
        g.TradeX.CloseTdx()
        g.TradeX.OpenTdx()
        client_id = g.TradeX.Logon(g.host, g.port, g.version, g.yybid, g.account_no,
                                      g.trade_account_no,
                                      g.password, g.tx_password,g.err)
        if client_id < 0:
            g.logger.error(u"登入交易服务器失败：{}".format(g.err.value.decode("GBK")))
            return None, g.err.value.decode("GBK")
        g.client_id = client_id
        g.logger.info(u"已登入交易服务器。")
        df, err = _QueryData(2)
#         if err == "":
#             g.market_account_no = {df.iloc[i][u'帐号类别']: df.iloc[i][u'股东代码'] for i in range(len(df))}            
    return client_id, g.err.value.decode("GBK")


def _logoff():
    '''
        试图登出
    :return: client_id, err
    '''

    client_id = g.get('client_id', -1)
    if client_id >= 0:
        g.logger.info(u"试图登出交易服务器...")
        g.TradeX.Logoff(client_id)
        del g.client_id
        g.logger.info(u"已登出交易服务器。")
    g.TradeX.CloseTdx()


def _QueryData(_type):
    '''
        查询各种交易数据
    :param _type:表示查询信息的种类， 0 资金 1 股份 2 当日委托 3 当日成交 4 可撤单 5 股东代码 6 融资余额 7 融券余额 8 可融证券 9 可申购新股查询 10 新股申购额度查询 11 配号查询 12 中签查询
    :return: (pd.DataFrame,err_info)
    '''

    # 试图登陆
    #client_id, err = _logon()
    #if client_id < 0:
        #return None, err

    # 获取数据
    g.TradeX.QueryData(g.client_id, _type ,g.res,g.err)
    if g.res == "":
        g.logger.error(u"获取数据失败：%s" % g.err.value.decode("GBK"))
        return None, g.err.value.decode("GBK")
#     print (StringIO(g.res.value))
    
    return pd.read_csv(StringIO(g.res.value), sep="\t", encoding="GBK"), ""

def _SendOrder(action, priceType,symbol, price, amount):
    '''
        委托交易下单
    :param action: 委托的种类:0 买入 1 卖出 2 融资买入 3 融券卖出 4 买券还券 5 卖券还款 6 现券还券
    :param priceType:报价方式:0 上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格 2(市价委托)深圳本方最优价格 3(市价委托)深圳即时成交剩余撤销 4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价
    :param symbol: 证券代码
    :param price: 委托价格 ,市价委托为0
    :param amount: 委托数量
    :return:
    '''

    # 试图登陆
    #client_id, err = _logon()
    #if client_id < 0:
        #return None, err

    # 市场 1 上海　0深圳
    mk_type = 1 if int(symbol[0]) >= 5 else 0
    #g.logger.info("market_account_no(%s)" % (g.market_account_no[mk_type]))
    g.TradeX.SendOrder(g.client_id , action, priceType, str(g.market_account_no[mk_type]),str(symbol), c_float(price), c_int(amount), g.res, g.err)
    if g.res.value=="":
        g.logger.error(u'委托交易下单失败：{}'.format(g.err.value.decode("gb2312")))
        return None,g.err.value.decode("gb2312")
    return pd.read_csv(StringIO(g.res.value), sep="\t", encoding="gb2312"), ""


def _cancel_order(exchange_id, order_id):
    if type(exchange_id) != list and type(order_id) != list:
        exchange_id = [exchange_id]
        order_id = [order_id]

    if len(exchange_id) != len(order_id):
        return None, u"参数错误，请检查代码！"

    # 试图登陆
    #client, err = _logon()
    #if client is None:
        #return None, err

    # CancelOrders() -> result 貌似只能批量撤除所有单，所以如果要批量撤除指定单只能一条条撤除
    for i in range(len(order_id)):
        g.TradeX.CancelOrder(g.client_id,int(exchange_id[i]), str(order_id[i]),g.res, g.err)
        #err, res = (err.decode("GBK"), res.decode("GBK"))
        if  g.err.value != "":
            g.logger.error(u'撤单失败,请手工撤单：%s' % g.err.value)
        g.logger.info(g.res)
    return u"撤单完成", ""

#def ipo():
    #g.logger.info(u"新股申购...")
    #_df, err = _QueryData(12)
    #if err != "":
        #g.logger.error(u"新股查询失败，请手工申购：%s"%err.decode("GBK"))
        #return
    #_df = _df[_df[u"参数"]>0]
    #g.logger.info(u"可申购新股数：%s"%len(_df))
    #fail_count = 0
    #for i in range(len(_df)):
        #_row = _df.iloc[i]
        #g.logger.info(u"_SendOrder(%s,%s,%s,%s,%s)"%(0, 0, _row[u"证券代码"], _row[u"委托价格"], _row[u"参数"]))
        #_, err = _SendOrder(0, 0, _row[u"证券代码"], _row[u"委托价格"], _row[u"参数"])
        #if err != "":
            #fail_count+=1
            #g.logger.error(u"新股[%s]申购失败，请手工申购：%s" % (_row[u"证券名称"],err.decode("GBK")))
    #g.logger.info(u"新股申购完毕%s。"%("" if fail_count==0 else u"[失败%s只]"%fail_count))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)-6s %(message)s')
    g.logger = logging.getLogger()
    g.err= create_string_buffer(256)
    g.res= create_string_buffer(1024*1024)  
    g.TradeX= windll.LoadLibrary("C:\\Users\\04yyl\\git\\lhjy\\deamo\\dlls\\trade_zx.dll")
    _logon()


