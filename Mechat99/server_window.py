# 过程：client首先通过一个套接字与server取得联系，第一次连接调用accept_wrapper，得到一个新的套接字用于之后的联系conn、和ip地址addr
# 通过sellector模块(self.sel)集合conn、events、key(套接字和定义的命名空间data(里面有addr，应用：可以用来收集这个接口发送的所有信息))在server中注册，关联
# 而后通过sellect()监听，识别出信号后，会有key和mask返回，如果已经注册过，使用key的fileobj(套接字)即可实现信息接收
# 当客户端发送数据到服务器时，触发 EVENT_READ，当服务器准备好发送数据回客户端时，触发 EVENT_WRITE
# 不同的客户端会触发不同的key
# 如果client断开了连接，会在server注销，key也会消失

import socket
import selectors
import types
from user import User,ViewUser
import threading
import time
import tkinter as tk
from client_window import Client
from window import MechatWindow
history_lock = threading.Lock()

# server连接关闭的依据：client连接的关闭会发送一个“结束”信号（FIN 包）到服务器，读取到空消息即可关闭连接

def RunServer_Window(Me:User,serverHost,serverPort,window:MechatWindow,client:Client,stop_event):
    #创建本地server
    myServer=Server(Me,serverHost,serverPort,window,client,stop_event)
    print("本地server已搭建")
    #打开server
    myServer.open()


class Server:
    def __init__(self,Me:User,serverHost,serverPort,window:MechatWindow,client:Client,stop_event) -> None:
        self.user= Me
        self.HOST=serverHost
        self.listenHOST = "0.0.0.0"  # 默认主机地址，如需修改需专门在runserver修改
        self.PORT = serverPort  # Port to listen on (non-privileged ports are > 1023)位于server上
        self.sel = selectors.DefaultSelector()
        self.window=window
        self.client=client
        self.stop_event=stop_event
        
    def open(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.bind((self.listenHOST, self.PORT))
            s.listen()
            print("等待连接")
            s.setblocking(False)
            self.sel.register(s, selectors.EVENT_READ, data=None)
            
            try:
                while not self.stop_event.is_set():  # 每次循环检查 stop_event
                    events = self.sel.select(timeout=1)  # 添加超时以避免长时间阻塞
                    for key, mask in events:
                        if key.data is None:
                            self.accept_wrapper(key.fileobj)
                        else:
                            self.service_connection(key, mask)
                    
                    # 可在此处添加其他逻辑处理，例如心跳包、超时检查等

            except KeyboardInterrupt:
                print("Caught keyboard interrupt, exiting")
            
            finally:
                self.sel.close()
                print("Server shut down.")
                
    def accept_wrapper(self,sock):
        
        conn, addr = sock.accept()  
        print(f"Server:A new connection from {addr} is set up")
        conn.setblocking(False)      
        self.responseFirstConnected(conn) #第一次连接要返回发送自己ID
        
        data = types.SimpleNamespace(ID=None,name=None,addr=addr,port=0, inb=b"", outb=b"") #使用命名空间对data进行封装
        #addr为一个元组，第一个元素是ip，第二个元素是client所使用的端口，但对server方来说，自己的client要连接的是对方打开的server接口，是不同的
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        
        time.sleep(1)
        for ID in self.client.serverConnecting:
            host=self.client.serverConnecting[ID][1]
            port=self.client.serverConnecting[ID][2]
            name=self.client.serverConnecting[ID][4]
            if (host==addr[0]):
                data.ID=ID
                data.port=port
                data.name=name
                return
        # received_data = conn.recv(1024).decode('utf-8').splitlines()#收到client信息  ！！！
        try:
            received_data = conn.recv(1024).decode('utf-8').splitlines()
            # 处理接收到的数据
        except BlockingIOError:
            # 处理没有可用数据的情况，比如等待下一次接收
            pass
        if(received_data[0]!='firstConnectTextFromClient'):
            print('Server: receive firstConnectTextFromClient go wrong')
        data.port=received_data[1]###################!!更新逻辑
        data.ID=received_data[2]
        data.name=received_data[3]
        print(f"server:{data.port}")
        print(data.ID)
        print(data.name)
        
        time.sleep(0.5)
        self.responseFirstConnected_Confirm(conn) #回复client,使client确定server已经接收到了信息
        print(f"Server:First connection with {data.ID}")
        #第一次连接中echo连接的反向连接:
        if data.ID!=self.user.ID:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((data.addr[0],int(data.port)))#port没有0开头，没有隐患
            #更新自己client的serverconnecting
            connectTime=time.perf_counter()
            self.client.serverConnecting.update({data.ID:(s,data.addr[0],data.port,connectTime,data.name)})
            print(f"server:serverConnecting:{self.client.serverConnecting}")
        
            #在界面中显示出连接信息：
            self.window.connectedtree.insert("", tk.END, values=(str(data.ID), addr,data.port))#更新connected窗口
        print(1)

        
    def responseFirstConnected(self,conn):
        # 第一次返回报文的格式：
        text="responseFirstConnected\n"
        text+=str(self.user.ID)+'\n'
        text+=self.user.name
        conn.sendall(text.encode('utf-8'))
        
    def responseFirstConnected_Confirm(self,conn):
        text="responseFirstConnected_Confirm"
        conn.sendall(text.encode('utf-8'))
        
    def service_connection(self,key, mask):
        conn = key.fileobj
        data = key.data
        addr=data.addr#获得该套接字的ip地址
        if mask & selectors.EVENT_READ:
            recv_data = conn.recv(1024).decode("utf-8")  
            if recv_data:
                self.showToSelf(addr,recv_data,conn,key)
            else:
                print(f"IP为{data.addr}的client断开了连接")
                self.sel.unregister(conn)
                conn.close()
        # if mask & selectors.EVENT_WRITE:
        #     self.responseToClient()
            

    def showToSelf(self,addr,text,conn,key):
        requestType=text.splitlines()[0]
        contentlist=text.splitlines()[1:]
        content = "\n".join(contentlist)
        ID=key.data.ID
        Name=key.data.name
        port=key.data.port
        print(requestType)

        if requestType=='message':  #发信息
            if self.user.isFriendbyID(ID):
                print(f"Friend Connected with {Name},ID is {ID}")
            else :
                print(f"Stranger Connected with {Name},ID is {ID}")
            if ID==self.user.ID:
                print("talk myself")
            else:
                with history_lock:
                    if ID not in self.user.chat_history:
                        self.user.chat_history[ID] = []  # 确保 ID 已存在
                    self.user.chat_history[ID].append(str(ID)+':'+content)
                    
                print(f"server:{content}")
                
                # 刷新chat_history
                self.window.show_chatHistory(Name)
                
                
        elif requestType=='addFriendsRequest':   #加好友请求
            resume=text.splitlines()[1:4]
            judge,_=self.user.findFriend_from_ID(resume[0])
            if judge:
                return
            #print(content)
            print("如果想同意好友请求，请输入y，如果不同意，请输入n")
            #result=input()
            self.window.addfriend_response_window()
            while self.window.continueToWait:
                1
            result=self.window.continueToWait_result
            if result=='y':
                self.window.returnToClient_continueToWait=False
                self.window.returnToClient_continueToWait_result='y'
                ID=resume[0]
                name=resume[1]
                newFriend=ViewUser(ID,name)
                self.user.friends.append(newFriend) #被申请者加好友
                self.responseToClientFriendRequest(ID)
                print("你同意了对方的好友申请")
                # 显示出好友信息
                #刷新在界面中的显示
                self.window.friendtree.insert("", tk.END, values=(ID, name, "connected"))  #状态更新未处理
                
            if result=='n':
                self.window.returnToClient_continueToWait=False
                self.window.returnToClient_continueToWait_result='n'
                refuseText="refuseFriendRequest"#############################更改
                refuseText+="Sorry,I refuse"
                conn.sendall(refuseText)
        elif requestType=="responseFriendRequest": #接收到好友申请的返回
            ID=key.data.ID
            getID=text.splitlines()[1]
            friendName=text.splitlines()[2]
            if ID==getID:
                newFriend=ViewUser(ID,friendName)
                self.user.friends.append(newFriend)
                return_window = tk.Toplevel(self.window.master)
                return_window.title("set_up_connection")
                tk.Label(return_window, text="加好友成功", padx=20, pady=20).pack()
                print(f"好友信息：ID:{ID},name:{friendName}")
                
                #刷新在界面中的显示
                self.window.friendtree.insert("", tk.END, values=(ID, friendName, "connected"))  #状态更新未处理
            else:
                print("He/She don't pass the secure test,please be cautious")
                print(f"And sender's IP is {addr}")
        elif requestType=="refuseFriendRequest": #接收到好友申请的拒绝
            print("The user refused your request")
                
    # 加好友的response报文：
    # responseFriendRequest
    # secure:                      该项是用来让client验证是否有伪装,内容为申请者的姓名
    # name:
    # ip:
    # port:
    def responseToClientFriendRequest(self,ID):
        conn=self.client.serverConnecting[ID][0]
        responseText="responseFriendRequest\n"
        responseText+=self.user.getResumeText()
        conn.sendall(responseText.encode('utf-8'))