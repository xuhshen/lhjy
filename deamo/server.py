import socket  
import threading  
import time  
import json
from lhjy.settings import SOCKET_SERVER,SOCKET_PORT   
    
class fundaccount(object):
    def __init__(self,username,passwd):
        pass

    def login(self):
        pass
    
    def logout(self):
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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.bind((SOCKET_SERVER, SOCKET_PORT))
    s.listen(8)
    while True:  
        sock, addr = s.accept()
        t = threading.Thread(target=handle, args=(sock,addr))  
        t.start()
        
        