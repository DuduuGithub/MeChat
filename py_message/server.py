import socket
import user

class Server:
    def __init__(self,Me) -> None:
        self.user= Me
        self.HOST = Me.addr  # 默认主机地址，如需修改需专门在此修改
        self.PORT = Me.port  # Port to listen on (non-privileged ports are > 1023)位于server上
        self.friend=None #如果不是friend,则就是none
        self.judge=False #True则表示是你的朋友
        self.client_addr="0"
        self.conn=0 # 实现多个连接时可以将此定义为列表
        
    def open(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.bind((self.HOST, self.PORT))
            s.listen()
            print("等待连接")
            
            conn, addr = s.accept()
            # conn是一个socket.socket对象，代表客户端之间的连接
            # conn.sendall()表示将内容发回客户端
            
            self.conn=conn
            self.client_addr=addr #这个addr表示client的地址
            
            
            self.judge,self.friend=self.user.findFriend_from_ip(addr)
            if self.judge:
                print(f"Connected with {addr},and is your friend,name is {self.friend.name}")
                
            else :
                print(f"Connected with {addr},and not your friend") #要加入引入自己这一user，显示出friends名并记入记录
            while True:
                data = self.conn.recv(1024)
                if not data:
                    self.conn.close()
                    return
                self.showToSelf(data)
                self.responseToClient()
    
    
    
    def showToSelf(self,data):
        if self.judge:
            print(f"{self.friend.name} : {data}")
            self.chat_history[self.friend].append(f"{self.friend.name} : {data}")
        else:
            print(f"{self.client_addr} : {data}")
            
    def responseToClient(self):
        self.conn.sendall(b"message is accepted")
        pass