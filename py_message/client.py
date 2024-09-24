# echo-client.py

import socket

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Connect(serverHost="127.0.0.1",serverPort=65432):
    
    #HOST、PORT指的都是server的主机与端口号
    HOST =  serverHost # 默认主机地址，如需修改需专门在此修改
    
    PORT = serverPort  # server的端口号

    # 当with块结束时，s会自动关闭，进而引发与之相连的server的conn会收到空字符，引发server的conn关闭
    # with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #     s.connect((HOST, PORT))
    #     s.sendall(b"Hello, world")
    #     data = s.recv(1024)
    #     print(f"Received {data!r}")
    
    #需要手动关闭
    s.connect((HOST, PORT))
        
def Close(serverHost="127.0.0.1",serverPort=65432):
    s.close()
    
def Send():
    message=input("输入message:")
    s.sendall(str.encode(message))
    
Connect()
for i in range(5):
    Send()
    data = s.recv(1024)
    print(f"Received {data!r}")
Close()
from main import myServer
myServer.close()