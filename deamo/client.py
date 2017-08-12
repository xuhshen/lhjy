import socket  
import time 
while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);  
    s.connect(('127.0.0.1', 9090));  
    print(s.recv(1024).decode('utf-8'));  
    time.sleep(0.1)
    for data in [b'lk', b'aa', b'bb']:  
        s.send(data);  
        s.send("{}".format({"a:123"}).encode());
        print(s.recv(1024).decode('utf-8'));  
    s.send(b'exit');  
    s.close();  
