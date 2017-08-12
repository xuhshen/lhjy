import socket  
import threading  
import time  
  
def tcplink(sock, addr):  
    print('Accept new connection from %s:%s...' % addr);  
    sock.send(b'Welcome!!!');  
    while True:  
        data = sock.recv(1024);  
#         time.sleep(1);  
        if not data or data.decode('utf-8') == 'exit':  
             break;  
        print (data.decode())
        sock.send(b'Hello, %s!' % data);  
    sock.close();  
    print('Connection from %s:%s closed.' % addr);  
  
if __name__ == "__main__":  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
    s.bind(('127.0.0.1', 9090));  
    s.listen(8); #监听8个客户端；  
    print('waiting for connection...');  
  
    while True:  
        sock, addr = s.accept();  
        t = threading.Thread(target=tcplink, args=(sock,addr));  
        t.start();  
        
        