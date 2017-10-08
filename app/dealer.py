from rest_framework.exceptions import ErrorDetail, ValidationError
import socket  
import json
from lhjy.settings import SOCKET_SERVER,SOCKET_PORT

def send2server(data):

    message = json.dumps(data).encode()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SOCKET_SERVER, SOCKET_PORT)) 
    
    s.send(message) 
    result = s.recv(1024).decode('utf-8')
    s.close()
    return json.loads(result)

def order2securities(data):
    '''下单到券商,返回委托单号，委托价，如果是市价委托，委托价为当前市价
              下单失败则直接返回异常
    '''
    message = {
               "account":data.get("strategy_account").capitalaccount.account_name,
               "code":data.get("trade_category").code,
               "action":data.get("trade_action").name,
               "number":data.get("pretrade_number"),
               "price":data.get("price"),
               "is_market_price":data.get("is_market_price"),
            }

    if message["action"] not in ["买入","卖出"]:
        raise ValidationError({"error":1,"message":"买卖动作错误，请检查数据库配置"})
  
    if data.get("strategy_account").capitalaccount.type.value == "回测账户":
        import uuid
        ticket = uuid.uuid1()
        price = data.get("price")
    else:
        try:
            rst = send2server(message)
            ticket = rst["ticket"]
            price = rst["price"]
        except:
            raise ValidationError({"error":1,"message":"下单失败，请检查网络状态，或者服务是否开启"})
    
    return ticket,price

def cancel_order2securities(data):
    '''撤销下单,如果正常取消，返回True，否则返回False，重复需要也返回False
     rst:{"message":True,"tradeprice":1，"tradenumber":1}
    '''
    message = {"action":"cancel","message":data} 
    
    try:
        rst = send2server(message)
        tradeprice = rst["tradeprice"]
        tradenumber = rst["tradenumber"]
    except:
        raise ValidationError({"error":1,"message":"cancel failed"})
    
    result = {"tradeprice":tradeprice,"tradenumber":tradenumber}
    
    return result

# def queryfromsecurities(data):
#     '''查询账户信息,返回字典，键值为委托单号，
#     '''
#     message = {"action":"query","message":data} 
#     
#     values = {
#               "ticket1":{"status":"","tradeprice":0,"tradenumber":0},
#               "ticket2":{"status":"","tradeprice":0,"tradenumber":0}
#               }
#     
#     return []

