from rest_framework.exceptions import ErrorDetail, ValidationError
import socket  
import time 
import json

def send2server(data):
    addr = "127.0.0.1"
    port = 9090
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
    s.connect((addr, port)) 
    b_data = json.dumps(data).encode()
    s.send(b_data) 
    result = s.recv(1024).decode('utf-8')
    s.close(); 
    return result

def order2securities(data):
    '''下单到券商
    data:{"act":"buy",data:<{}>} 
    '''
    ticket = send2server(data)
    price = 100
    try:
        ticket = send2server(data)
    except:
        raise ValidationError({"error":1,"message":"ordering failed"})
    return ticket,price

def cancel_order2securities(data):
    '''撤销下单,如果正常取消，返回True，否则返回False，重复需要也返回False
    '''
    try:
        rst = send2server(data)
    except:
        raise ValidationError({"error":1,"message":"cancel failed"})
    return rst



