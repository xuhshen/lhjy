from rest_framework.exceptions import ErrorDetail, ValidationError
import socket  
import time 
import json
from lhjy.settings import SOCKET_SERVER,SOCKET_PORT

#done
def send2server(data):

    message = json.dumps(data).encode()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SOCKET_SERVER, SOCKET_PORT)) 
    
    s.send(message) 
    result = s.recv(1024).decode('utf-8')
    s.close()
    
    return json.loads(result)
#done
def order2securities(data):
    '''下单到券商,返回委托单号，委托价，如果是市价委托，委托价为当前市价
              下单失败则直接返回异常
    '''
    message = {"action":"order","message":data} 
    market_price = data[0].get("market_price",False)
    
    if not market_price:
        price = data[0].get("price",False)
        if not price:
            raise ValidationError({"error":1,"message":"price or market_price should be privide"})
    try:
        rst = send2server(message)
        ticket = rst["ticket"]
        price = rst["price"]
    except:
        raise ValidationError({"error":1,"message":"ordering failed"})
    
    return ticket,price
#done
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

def queryfromsecurities(data):
    '''查询账户信息,返回字典，键值为委托单号，
    '''
    message = {"action":"query","message":data} 
    
    values = {
              "ticket1":{"status":"","tradeprice":0,"tradenumber":0},
              "ticket2":{"status":"","tradeprice":0,"tradenumber":0}
              }
    
    return []

