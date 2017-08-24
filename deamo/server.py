import socket  
import threading  
import time  
import json
from lhjy.settings import SOCKET_SERVER,SOCKET_PORT   
from functools import wraps   

class fundaccount(object):
    
    def __init__(self,username=None,passwd=None):
        self.ongoing_ticket = []
        self.username = username
        self.passwd = passwd
        self.conntect = None
        
    def login(self):
        self.conntect = 12345
        return self.conntect
    
    def connection(self=None):
        def decorate(func):
            def wrapper(self,*args, **kwargs):
                if self.ongoing_ticket == []:
                    self.login()
                return func(self,*args, **kwargs)
            return wrapper
        return decorate
    
    def logout(self):
        pass
    
    
    def cancel(self,data):
        self.conntect(data)
        return 
    
    @connection()
    def query_order_ticket(self):
        '''查询当日委托单
        '''
        print (self.conntect)
    
    def update_ticket_queue(self,ticket,add=True):
        '''更新给个账户未完成委托单队列列表'''
        if add:
            self.ongoing_ticket.append(ticket)
        else:
            self.ongoing_ticket.remove(ticket)
     
    def update_dashboard(self,data):
        '''同步更新本地交易系统状态
        '''
        pass
    
    def syncdb(self):
        order_ticket = self.query_order_ticket()
        for ticket in self.ongoing_ticket:
            if order_ticket.get(ticket,None):
                if order_ticket["ticket"]["status"] in ["deal","cancel"]:
                    self.update_ticket_queue(ticket,add=False)
                    self.update_dashboard(order_ticket[ticket])
                elif order_ticket["ticket"]["status"] == "partail deal":
                    self.update_dashboard(order_ticket[ticket])
        return             
    
    def run(self):
        while self.ongoing_ticket:
            pass
    
                
#done
def handle(sock, addr):  
    print('Accept new connection from %s:%s...' % addr) 
    data = sock.recv(1024)
    rst = parse_data(json.loads(data.decode()))   
    sock.send(rst)
    sock.close()

def parse_data(data):
    action = data.get("action","")
    if action == "cancel":
        message = {"message":True,"trademoney":0,"tradenumber":0}
        
    elif action == "order":
        ticket = str(time.time())
        message = {"ticket":ticket,"price":10}
        
    elif action == "query":
        message = {}
        
    else:
        message = {}
    
    rst = json.dumps(message).encode()
    return rst



  
if __name__ == "__main__":  
    
    a=fundaccount()
    a.query_order_ticket()
#     
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
#     s.bind((SOCKET_SERVER, SOCKET_PORT))
#     s.listen(8)
#     
#     while True:  
#         sock, addr = s.accept()
#         t = threading.Thread(target=handle, args=(sock,addr))  
#         t.start()
#         
        