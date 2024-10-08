#某一时刻只会与一个主机进行联系
# 规定，发送信息的第一行表示该请求的命令名称
# serverConnecting是client使用用于管理已连接conn的，
# 连接到server的client会自动建立一个朝向对应server的连接，放入serverConnecting，第一次连接会受到返回信息进而确定ID
#即使通过friend的相关信息来连接，也对已连接的对象
# 聊天记录所有人的都会保存
#改名需要重新连接所有连接
import socket
from user import User
import time
import threading
import tkinter as tk
from YourInformation import yourUsingPort
dict_lock = threading.Lock()
Me_lock=threading.Lock()


def RunClient_Window(Me):
    client=Client()
    client.runClient(Me)
    
class Client:
    def __init__(self) -> None:
        self.serverConnecting={}  #ID:(conn,ip,port,time,name) 元组为不可改变的对象，当更新time时，要更新serverConnnecting
        self.firstConnectedID=0  # 用于接受第一次返回的ID
        self.targetHost=0#这两个每次连接都要更新
        self.targetPort=0
        
    def findIDfromIP(self,ip):
        for id,tuple in self.serverConnecting.items():
            if tuple[1]==ip:
                return True,id
        return False,0
    def help():
        pass
    
    def refreshConnect(self,name):
        for ID,tuple in self.serverConnecting.items():
            conn=tuple[0]
            serverHost=tuple[1]
            serverPort=tuple[2]
            conn.close()
            connectTime=time.perf_counter()
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((serverHost,serverPort))
            self.serverConnecting[ID]=(conn,serverHost,serverPort,connectTime,name)
        pass
    
    def changeName(self,Me,newName):
        Me.name=newName
        self.refreshConnect(newName)
        
    def show_serverConnecting(self):
        for id,tupple in self.serverConnecting.items():
            print(id+':'+str(tupple))
        pass
    

    
    #  ****************Run**************************
    def runClient(self,Me:User):  #新学写法，指定函数形参的类型
        self.helloToUSer()
        print('Resume'+Me.getResumeText())
        while True:
            self.selectToClose() # 在此关闭连接
            command=input("请输入指令(输入help可以获得指令介绍)").lower() #会整行输入,Lower之后大小写不敏感
            if command=="help":
                help()
            elif (command=="message with stranger")|(command=="message by ip"):
                
                
                serverHost=input("输入server的IP地址:")
                serverPort=int(input("输入对应server的端口号:"))
                messageAdd=input("输入想发送的内容：")
                self.message_by_ip(serverHost,serverPort,messageAdd,Me)
                
            elif (command=="message by id"):
                serverID=input("输入联系对象的ID:")
                if serverID not in self.serverConnecting:
                    print("已连接设备中没有找到该ID")
                else:
                    messageAdd=input('输入想发送的内容:')
                    self.message_by_ID(serverID,messageAdd,Me)
                    
            elif (command=="message by friendname"):
                FriendName=input("输入您想要连接的friend的name:")
                judge,_=Me.findFriend_from_name(FriendName)
                if judge==False:
                    print("您没有这样的好友，请重新输入指令")
                else:
                    print("找到了好友")
                    messageAdd=input(Me.name+':')
                    self.message_by_friendname(Me,FriendName,messageAdd)
                    print("已发送")
                    
            # 窗口中，点击某个对象的add friends按钮，能获取addr再调用此函数加
            elif (command=="add friends")|(command=="add friend"):
                requestAddr=input("输入对方的IP地址:")
                requestPort=int(input("输入对方的端口号:"))
            
                requestTextAdd=Me.getResumeText()
                requestTextAdd+=input("输入申请语:")
                self.addFriendRequest(requestAddr,requestPort,requestTextAdd,Me)
                
            elif (command=="exit")|(command=="quit"):
                break
            elif command=="history":
                name=input("请输入要查看聊天的朋友name:")
                self.showHistorybyName(name,Me)
            elif command=="show connecting":
                self.show_serverConnecting()
            elif command=="change name":
                    Newname=input('输入想要改成的名字：')
                    self.changeName(Me,Newname)
            else:
                print("unknown command")     
    
    #***********************Run end**********************************
    def helloToUSer(self):
        text="Hi~Welcome to Mechat Client"
        print(text)
        
    def firstConnectTextFromClient(self,conn,Me:User):
        message='firstConnectTextFromClient\n'
        message+=str(yourUsingPort)+'\n' #!!!!!!!!!!!!!!!!!!添加逻辑
        message+=Me.getResumeText()
        conn.sendall(message.encode('utf-8'))
        
    def connect_if_not_exisits(self,serverHost,serverPort,Me:User):

        serverPort_int=int(serverPort)
        print(f"client:{serverHost},{serverPort_int}")
        print(self.serverConnecting)
        for _,host,port,_,_ in self.serverConnecting.values():
            if (host==serverHost) | (port==serverPort_int):
                return False
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((serverHost,serverPort_int))
        except socket.error as e:
            print(f"Connection error: {e}")  # 处理连接错误
            return None  # 连接失败时返回 None
        
        self.firstConnectTextFromClient(s,Me) #向server发送自己的信息
        print("Client:Connecting...")
        while True:
            try:
                data = s.recv(1024)
                if not data:
                    print("Client:连接已关闭")
                    break
                content=data.decode('utf-8').splitlines()
                if content[0]=="responseFirstConnected":
                    print("Client:responseFirstConnected:", content[1])
                    ID=content[1]
                    name=content[2]
                    self.firstConnectedID=content[1]
                    break;
            except Exception as e:
                print("接收数据时发生错误:", e)
                break
        while True:
            try:
                data = s.recv(1024)
                if not data:
                    print("Client:连接已关闭")
                    break
                content=data.decode('utf-8')
                if content=="responseFirstConnected_Confirm":
                    break
            except Exception as e:
                print("接收数据时发生错误:", e)
                break
        print("Client:first connected compleated")
        #更新severconnecting
        connectTime=time.perf_counter()
        self.serverConnecting.update({ID:(s,serverHost,serverPort_int,connectTime,name)})
        print(f"serverConnecting:{self.serverConnecting}")
        return True
    
    #TCP允许持续连接，使用持续连接，以实现低延迟的通信,设定5min无操作的话断开连接 
    def refreshTime(self,ID):
        # 更新时间
        nowTime=time.perf_counter()
        conn,ip,port=self.serverConnecting[ID][:3]
        name=self.serverConnecting[ID][4]
        self.serverConnecting[ID]=(conn,ip,port,nowTime,name)
    
    def selectToClose(self):
        for ID,mylist in self.serverConnecting.items():
            lastTime=mylist[-2]
            timeNow=time.perf_counter()
            if timeNow-lastTime>60*10:
                conn=mylist[0]
                conn.close()
                del self.serverConnecting[ID]
        pass
    
    
    # 一个可移植函数，要保证里面的内容直接且无冗杂
    def Send_by_ID(self,ID,messageFinal,Me:User):
        print("messagefinal: "+messageFinal)
        print(ID)
        print(self.serverConnecting)
        self.serverConnecting[ID][0].sendall(messageFinal.encode('utf-8'))
        self.refreshTime(ID)
        print("已发送")
        contentlist=messageFinal.splitlines()[1:]
        content='\n'.join(contentlist)
        # 聊天记录
        with Me_lock:
            time.sleep(0.5)
            if ID not in Me.chat_history:
                Me.chat_history[ID] = []  # 确保 ID 已存在
            else:
                print('right')
            Me.chat_history[ID].append(Me.ID+':'+content)
            print("chat_history updates")
            print(Me.chat_history)
    
    def Send_by_ip(self,serverHost,serverPort,messageFinal,Me):
        self.connect_if_not_exisits(serverHost,serverPort,Me)
        judge,ID=self.findIDfromIP(serverHost)
        if judge:
            self.Send_by_ID(ID,messageFinal,Me)
        else:
            print("error in Send_by_ip")
        
    # 这俩只是套壳
    def message_by_ID(self,ID,messageAdd,Me:User):
        message="message\n"  #命令名
        message+=messageAdd
        self.Send_by_ID(ID,message,Me)

    def message_by_ip(self,serverHost,serverPort,messageAdd,Me):
        message="message\n"  #命令名
        message+=messageAdd
        self.Send_by_ip(serverHost,serverPort,message,Me)
        
    def message_by_friendname(self,Me,name,messageAdd):
        for tupple in Me.friends:
            if tupple.name==name:
                id=tupple.ID
        self.message_by_ID(id,messageAdd,Me)
    
    
    def receive_data(self, conn):
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print("连接已关闭")
                    break
                print("接收到消息:", data.decode('utf-8'))
                self.firstConnectedID=data.decode('utf-8')
            except Exception as e:
                print("接收数据时发生错误:", e)
                break
            
    # 接下来需要再server中写出接受好友请求函数，需要在kongzhitai输入y\n，并返回给client结果，client再依次进行好友添加
    # 好友请求报文的格式：
    # addFriendsRequest
    # ID
    # name
    # {申请语}
    # n请求添加你为好友
    def addFriendRequest(self,requestAddr,requestPort,requestTextAdd,Me:User):
        judge=self.connect_if_not_exisits(requestAddr,requestPort,Me)#还有当输入addrport出现错误时的信息没写出
        _,ID=self.findIDfromIP(requestAddr)
        judge,_=Me.findFriend_from_ID(ID)
        if judge:
            print(f"他/她已经是你的好友力")
            return
        requestText="addFriendsRequest\n" #命令名
        requestText+=requestTextAdd
        requestText+='\n请求添加你为好友'
        print(requestText)
        self.Send_by_ip(requestAddr,requestPort,requestText,Me)
        
        print("好友申请已发送")
        
        
    
    def getHistorybyID(self,ID,Me:User):
        judge=ID in Me.chat_history
        if judge==False:
            return False,None
        else:
            return True,Me.chat_history[ID]
        
            
    def getHistorybyName(self,name,Me:User):
        judge,friend=Me.findFriend_from_name(name)
        if judge:
            self.showHistorybyID(friend.ID,Me)
        else:
            print("未找到此人")
    
