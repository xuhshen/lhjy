import socket  
import threading  
import time  
import json
from lhjy.settings import SOCKET_SERVER,SOCKET_PORT   
import requests
from multiprocessing import Process
import os
import sys
import logging

basedir = os.path.dirname(sys.argv[0])
logfile = os.path.join(basedir,"sys.log")
TOKEN = "Token 7729b1a47d79817903aba023af936090adecee38" 
QUERY_URL = "http://127.0.0.1:8000/query/0/"
UPDATE_BASE_URL = "http://127.0.0.1:8000/query/"

logger = logging.getLogger('deamo')
# logging.basicConfig(filename=logfile,level=logging.DEBUG,filemode='a',)
logger.setLevel(logging.DEBUG)

# create a handler, write to log.txt
# logging.FileHandler(self, filename, mode='a', encoding=None, delay=0)
# A handler class which writes formatted logging records to disk files.
fh = logging.FileHandler(logfile)
fh.setLevel(logging.DEBUG)

# create another handler, for stdout in terminal
# A handler class which writes logging records to a stream
# sh = logging.StreamHandler()
# sh.setLevel(logging.DEBUG)

# set formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# sh.setFormatter(formatter)
# add handler to logger
logger.addHandler(fh)
# logger.debug('Debug')
# logger.info('Info')

class dashboard(object):
    def __init__(self,token=TOKEN,query_url=QUERY_URL,base_update_url=UPDATE_BASE_URL):
        self.token = token
        self.query_url = query_url
        self.header = {"Authorization": self.token,}
        self.base_update_url = base_update_url
    
    
    def query_pending_tickets(self,):
        try:
            r = requests.get(self.query_url,headers=self.header)
            result = json.loads(r.text)
        except:
            result = []
        return result
    
    def format_account_data(self,query):
        '''调整数据格式，{账号：{委托单号：记录}}
        '''
        rst = {}
        for item in query:
            if rst.__contains__(item["account"]):
                rst[item["account"]][item["market_ticket"]] = item
            else:
                rst[item["account"]] = {item["market_ticket"]:item}
        return rst

    def update_ticket(self,buildid,data):
        '''同步券商账户信息到本地数据库
        data：{ "status": "","name": "","tradeprice": null,"tradenumber": null,}
        '''
        
        url = "{}/{}/".format(self.base_update_url,buildid)
        rst = requests.post(url,data,headers=self.header)
        return rst

 
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
        '''从券商查询当日委托单
        '''
        print (self.conntect)
    
    def update_ticket_queue(self,ticket,add=True):
        '''更新给个账户未完成委托单队列列表'''
        if add:
            self.ongoing_ticket.append(ticket)
        else:
            self.ongoing_ticket.remove(ticket)
     
    def update_dashboard(self,data,dashboard):
        '''同步更新本地交易系统状态
        '''
        dashboard.update_ticket()
    
#     def syncdb(self,dashboard):
#         order_ticket = self.query_order_ticket()
#         for ticket in self.ongoing_ticket:
#             if order_ticket.get(ticket,None):
#                 if order_ticket["ticket"]["status"] in ["deal","cancel"]:
#                     self.update_ticket_queue(ticket,add=False)
#                     self.update_dashboard(order_ticket[ticket])
#                 elif order_ticket["ticket"]["status"] == "partail deal":
#                     self.update_dashboard(order_ticket[ticket],dashboard)
#         return             
#     
#     def run(self):
#         while self.ongoing_ticket:
#             pass
    
                
#done
def handle(sock, addr,dealer_connect):  
    logger.info('Accept new connection from %s:%s...' % addr) 
    data = sock.recv(1024)
    rst = parse_data(json.loads(data.decode()),dealer_connect)   
    sock.send(rst)
    sock.close()

def parse_data(data,dealer_connect):
    action = data.get("action","")
    if action == "cancel":
        message = {"message":True,"trademoney":0,"tradenumber":0}
        
    elif action == "order":
        ticket = str(time.time())
        message = {"ticket":ticket,"price":10}
        logger.info (dealer_connect)
        
    elif action == "query":
        message = {}
        
    else:
        message = {}
    
    rst = json.dumps(message).encode()
    return rst


class mydeamo(object):
    def __init__(self,socket_server=SOCKET_SERVER, socket_port=SOCKET_PORT,):
        self.socket_server = socket_server
        self.socket_port = socket_port
        self.socket = None
        self.dashboard = dashboard()
        self.sleeptime = 10
    
    def _start_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.socket_server, self.socket_port))
        self.socket.listen(8)    
    
    def _start_sync_server(self,dealer_connect):
        order_monitor = threading.Thread(target=self._monitor_order,args=(dealer_connect,))
        order_monitor.setDaemon(False)
        order_monitor.start()
        return order_monitor
        
    def _monitor_order(self,dealer_connect):
        while True:
            try:
                tickets = self.dashboard.query_pending_tickets()
                if not tickets:
                    logger.info("no unfinished recored, exit thread!")
                    break #如果没有未完成交易数据，进入休眠
                formatdata = self.dashboard.format_account_data(tickets)
                
                for account,tickets in formatdata.items():
                    if not dealer_connect.__contains__(account):
                        dealer_connect[account] = fundaccount(username=account)
                    dealer_connect[account].query_order_ticket()
            except Exception as e :
                logger.debug(e)
            
            time.sleep(self.sleeptime)
    
    def start_server(self):
        '''开启socket 服务，同时轮询dashboard
        '''
        dealer_connect = {} #保存各个券商的连接对象，避免重复连接，键值为资金账户
        
        self._start_socket() #启动socket监听
        order_monitor = self._start_sync_server(dealer_connect) #启动券商和数据库同步服务
        
        #获取监听数据，执行对应的下单和撤单任务
        while True:
            sock, addr = self.socket.accept()
            if not order_monitor.isAlive(): #检查线程是否还存活
                order_monitor = self._start_sync_server(dealer_connect)
            t = threading.Thread(target=handle, args=(sock,addr,dealer_connect))  
            t.start()
  
if __name__ == "__main__":  
    
    deamo = mydeamo()
    deamo.start_server()
#     






        