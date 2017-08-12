import socket  
import threading  
import time  
import json
  
    
class fundaccount(object):
    def __init__(self,username,passwd):
        pass

    def login(self):
        pass
    
    def logout(self):
        pass

def tcplink(sock, addr):  
    print('Accept new connection from %s:%s...' % addr) 
    data = sock.recv(1024)
    s_data = data.decode()
    d = json.dumps(addr).encode()
    sock.send(d)
    sock.close()
  
if __name__ == "__main__":  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.bind(('127.0.0.1', 9090))
    s.listen(8)
    while True:  
        sock, addr = s.accept()
        t = threading.Thread(target=tcplink, args=(sock,addr))  
        t.start()
        
        