import tkinter as tk
from tkinter import scrolledtext, ttk
from user import User,ViewUser
from YourInformation import yourIPv4Addr, yourUsingPort, yourName,yourID
from client_window import Client
import threading

class UsersInWindow:
    def __init__(self, ID, name, isConnected="offline", addr=None,port=None):
        self.ID = ID
        self.name = name
        self.isConnected = isConnected
        self.addr=addr
        self.port=port
        
def sewID(probablyBrokenID):
        probablyBrokenID_str=str(probablyBrokenID)
        Len=len(probablyBrokenID_str)
        if Len<4:
            probablyBrokenID_str='0'*(4-Len)+probablyBrokenID_str
        return probablyBrokenID_str
class MechatWindow:
    def __init__(self, master,client:Client,Me:User):
        self.master = master
        master.title("Mechat")
        self.client=client
        self.user=Me
        
        self.targetID_clicking=0
        
        # 创建一个框架来容纳按钮
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side="left", padx=10, pady=10)
        # 连接 button
        self.set_up_connection_button = tk.Button(self.button_frame, text="connect",bg="lightblue", fg="black", width=10, height=2, command=self.set_up_connection_window) #直接指定函数不能有参数
        self.set_up_connection_button.pack(pady=10,padx=10)
        # 加好友 button
        self.add_friend_button=tk.Button(self.button_frame, text="add friend",bg="lightblue", fg="black", width=10, height=2, command=self.add_friend_window) #直接指定函数不能有参数
        self.add_friend_button.pack(pady=10,padx=10)
        #快捷加好友button
        self.add_friend_button = None
        
        #收到加好友消息弹窗的组件
        self.response_addfriend_window=None
        self.response_addfriend_entry=None
        self.continueToWait=True
        self.continueToWait_result=None
        # self.returnToClient_continueToWait=True
        # self.returnToClient_continueToWait_result=None
        
        
        # 右侧好友列表
        self.friends_frame = tk.Frame(master, width=150)  # 缩小左侧框的宽度
        self.friends_frame.pack(side="right", fill="both",expand=False)
        
        # 左侧连接的主机列表
        self.connected_frame = tk.Frame(master, width=150)  # 也缩小右侧框的宽度
        self.connected_frame.pack(side="left", fill="both",expand=False)

        # 创建好友Treeview
        self.friendtree = ttk.Treeview(self.friends_frame ,columns=("ID", "Name", "Status"), show='headings')
        self.friendtree.heading("ID", text="ID")
        self.friendtree.heading("Name", text="Name")
        self.friendtree.heading("Status", text="Status")
        self.friendtree.column("ID", width=50)
        self.friendtree.column("Name", width=80)
        self.friendtree.column("Status", width=90)
        self.friendtree.pack(padx=5, pady=10, fill="both", expand=True)
        
        self.friends_label = tk.Label(self.friends_frame, text="好友列表", font=("Arial", 14, "bold"), bg="lightgray")
        self.friends_label.pack(pady=5) 

        # 创建连接的主机Treeview
        self.connectedtree = ttk.Treeview(self.connected_frame, columns=("ID", "Addr", "Port"), show='headings')
        self.connectedtree.heading("ID", text="ID")
        self.connectedtree.heading("Addr", text="Addr")
        self.connectedtree.heading("Port", text="Port")
        self.connectedtree.column("ID", width=50)
        self.connectedtree.column("Addr", width=80)
        self.connectedtree.column("Port", width=90)
        self.connectedtree.pack(padx=5, pady=10, fill="both", expand=True)
        
        self.connected_label = tk.Label(self.connected_frame, text="连接的主机", font=("Arial", 14, "bold"), bg="lightgray")
        self.connected_label.pack(pady=5)  # 添加一些上边距

        # 添加初始好友
        self.friendtree.insert("", tk.END, values=(self.user.ID, self.user.name, "unconnected"))
        for viewuser in Me.friends[1:]:
            self.friendtree.insert("", tk.END, values=(viewuser.ID, viewuser.name, "unconnected"))

        # 中间聊天记录显示框
        self.chat_display = scrolledtext.ScrolledText(master, width=60, height=20)  # 增大聊天框的宽度
        self.chat_display.pack(side="top", padx=10, pady=10, fill="both", expand=True)

        # 底部输入框和发送按钮
        self.input_frame = tk.Frame(master)
        self.input_frame.pack(side="bottom", fill="x")

        # 使用 Text 组件替代 Entry 组件来增加高度
        self.message_entry = tk.Text(self.input_frame, height=10, width=80)  # 增加高度和宽度
        self.message_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)

        self.send_button = tk.Button(self.input_frame, text="发送", command=self.send_message)
        self.send_button.pack(side="right", padx=10)



        
        
        # 绑定好友选择事件
        self.friendtree.bind("<<TreeviewSelect>>", self.click_Friendlyhost)
        self.connectedtree.bind("<<TreeviewSelect>>", self.click_Connectedhost)
        
        # 启动定时器，检查连接
        self.check_connections()

    def set_up_connection_window(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("发送到指定地址")

        tk.Label(self.window, text="地址:").grid(row=0, column=0, padx=10, pady=10)
        self.address_entry = tk.Entry(self.window)
        self.address_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.window, text="端口:").grid(row=1, column=0, padx=10, pady=10)
        self.port_entry = tk.Entry(self.window)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10)

        self.connect_button = tk.Button(self.window, text="连接", command=self.set_up_connection_window_run)
        self.connect_button.grid(row=3, columnspan=2, pady=10)
        
    def add_friend_window(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("加好友")

        tk.Label(self.window, text="地址:").grid(row=0, column=0, padx=10, pady=10)
        self.address_entry = tk.Entry(self.window)
        self.address_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.window, text="端口:").grid(row=1, column=0, padx=10, pady=10)
        self.port_entry = tk.Entry(self.window)
        self.port_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(self.window, text="申请语:").grid(row=2, column=0, padx=10, pady=10)
        self.messageAdd_entry = tk.Entry(self.window)
        self.messageAdd_entry.grid(row=2, column=1, padx=10, pady=10)

        self.connect_button = tk.Button(self.window, text="加！", command=self.add_friend_window_run)
        self.connect_button.grid(row=3, columnspan=2, pady=10)

    def set_up_connection_window_run(self):
        addr=self.address_entry.get()
        port=int(self.port_entry.get())
        judge=self.client.connect_if_not_exisits(addr,port,self.user)
        judge_window = tk.Toplevel(self.master)
        judge_window.title("set_up_connection")
        if judge:
            tk.Label(judge_window, text="连接成功。", padx=20, pady=20).pack()
            _,ID=self.client.findIDfromIP(addr)
            self.connectedtree.insert("", tk.END, values=(str(ID), addr,port))#更新connected窗口
            #更新friend窗口
            for item in self.friendtree.get_children():  # 遍历 Treeview 中的所有项
                friend_info = self.friendtree.item(item)["values"]  # 获取每一项的值
                print(friend_info[0])
                print(ID)
                friendID=sewID(friend_info[0])
                if  friendID== ID:  # 检查 ID 是否匹配
                    # 更新状态
                    self.friendtree.item(item, values=(str(friendID), friend_info[1], "connected"))
                    break  # 找到并更新后可以跳出循环
        else :
            tk.Label(judge_window, text="连接失败。", padx=20, pady=20).pack()
        tk.Button(judge_window, text="关闭", command=judge_window.destroy).pack(pady=10)

    #可移植函数
    def add_friends(self,addr,port,messageAdd): 
        self.client.addFriendRequest(addr,port,messageAdd,self.user)
        judge_window = tk.Toplevel(self.master)
        judge_window.title("set_up_connection")
        tk.Label(judge_window, text="好友申请已发送。", padx=20, pady=20).pack()
        # while self.returnToClient_continueToWait:
        #     1
        # if self.returnToClient_continueToWait_result=='y':
        #     print("对方同意了你的好友申请")
        # else:
        #     print("对方未同意您的好友申请")
        # self.add_friend_return_window()
        # self.returnToClient_continueToWait=True
        # self.returnToClient_continueToWait_result=None
            
        
        
    def add_friend_window_run(self):
        addr=self.address_entry.get()
        port=int(self.port_entry.get())
        messageAdd=self.user.getResumeText()
        messageAdd+=self.messageAdd_entry.get()
        self.add_friends(addr,port,messageAdd)
        
        
    def add_friend_quickly(self):
        selected_item = self.connectedtree.selection()[0]
        host_info = self.connectedtree.item(selected_item)["values"]
        addr=host_info[1]
        port=host_info[2]
        messageAdd=self.user.getResumeText()
        self.add_friends(addr,port,messageAdd)
        
    def addfriend_response_window(self):
        # 创建一个新的弹出窗口
        self.response_addfriend_window = tk.Toplevel(self.master)
        self.response_addfriend_window.title("好友申请")

        # 创建一个标签显示申请信息
        label = tk.Label(self.response_addfriend_window, text="你收到了一个好友申请，是否同意？(y/n)")
        label.pack(padx=20, pady=10)

        # 输入框
        self.response_addfriend_entry = tk.Entry(self.response_addfriend_window)
        self.response_addfriend_entry.pack(padx=20, pady=10)

        # 确认按钮
        confirm_button = tk.Button(self.response_addfriend_window, text="确定", command=self.response_friend_request)
        confirm_button.pack(pady=10)
        
    def response_friend_request(self):
        result=self.response_addfriend_entry.get()
        result_window = tk.Toplevel(self.master)
        result_window.title("set_up_connection")
        self.continueToWait=False
        if result=='y':
            self.continueToWait_result='y'
            tk.Label(result_window, text="加好友成功。", padx=20, pady=20).pack()
        else:
            self.continueToWait_result='n'
            tk.Label(result_window, text="已拒绝。", padx=20, pady=20).pack()
            
    # def add_friend_return_window(self):
    #     returnWindow=tk.Toplevel(self.master)
    #     returnWindow.title("好友申请结果")
    #     if self.returnToClient_continueToWait_result=='y':
    #         tk.Label(returnWindow, text="加好友成功。", padx=20, pady=20).pack()
    #     else:
    #         tk.Label(returnWindow, text="对方未同意你的好友申请", padx=20, pady=20).pack()
         
         
         
    def check_connections(self):
        """ 定时检查连接状态并关闭超时的连接 """
        self.client.selectToClose()  # 检查并关闭连接
        self.master.after(10000, self.check_connections)  # 每10秒检查一次
        
    def send_message(self):
        messageAdd = self.message_entry.get("1.0", "end-1c")
        print(self.targetID_clicking)
        self.client.message_by_ID(self.targetID_clicking,messageAdd,self.user)
        for ID in self.client.serverConnecting:
            if self.targetID_clicking==ID:
                name=self.client.serverConnecting[ID][4]
        
        #刷新界面
        self.show_chatHistory(name)

         # 清空输入框
        self.message_entry.delete(1.0, tk.END)
        
    def show_chatHistory(self,host_name): #可移植函数
        judge,history=self.client.getHistorybyID(self.targetID_clicking,self.user)
        #显示
        self.chat_display.delete(1.0, tk.END)
        if judge:
            for passage in history:
                contentlist=passage.split(':',1)
                ID=contentlist[0]
                content=contentlist[1]
                if ID==self.user.ID:
                    name=self.user.name
                else:
                    name=host_name
                self.chat_display.insert(tk.END,str(name)+':'+content+'\n')
        else:
            self.chat_display.insert(tk.END,"你们还没聊过天\n")
    def click_Friendlyhost(self,event):
        
        if not self.friendtree.selection():
            return  # 如果没有选中项，直接返回
        
        selected_item = self.friendtree.selection()[0]
        
        # 清除其他选中项
        for item in self.connectedtree.selection():
            self.connectedtree.selection_remove(item)
        if len(self.friendtree.selection())==2:
            selected_to_clear_item = self.friendtree.selection()[0]
            self.friendtree.selection_remove(selected_to_clear_item)
        
        
        host_info = self.friendtree.item(selected_item)["values"]
        self.targetID_clicking=sewID(host_info[0])
        host_name=host_info[1]
        host_status=host_info[2]
        
        # 更新窗口标题为当前好友名称
        self.master.title(f"Mechat - {host_name}")
        
        self.show_chatHistory(host_name)
            
        if self.add_friend_button:
            self.add_friend_button.destroy()
            
        if host_status == "connected":
            self.message_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            self.send_button.pack(side="right", padx=10)
        else:
            self.message_entry.pack_forget()  # 隐藏输入框
            self.send_button.pack_forget()  # 隐藏发送按钮
            self.chat_display.insert(tk.END,"ta还未上线,建议去线下真实")
            
            
    
        
    def click_Connectedhost(self,event):
        if not self.connectedtree.selection():
            return  # 如果没有选中项，直接返回
        selected_item = self.connectedtree.selection()[0]
        
        # 清除其他选中项
        for item in self.friendtree.selection():
            self.friendtree.selection_remove(item)
        if len(self.connectedtree.selection())==2:
            selected_to_clear_item = self.connectedtree.selection()[1]
            self.connectedtree.selection_remove(selected_to_clear_item)
        
        
        host_info = self.connectedtree.item(selected_item)["values"]
        self.targetID_clicking=sewID(host_info[0])
        print(self.targetID_clicking)
        host_ip=host_info[1]
        
        # 更新窗口标题为当前好友名称
        self.master.title(f"Mechat - {host_ip}")
        
        self.show_chatHistory(host_ip)
        
        if self.add_friend_button:
            self.add_friend_button.destroy()

        # 动态添加加好友按钮
        self.add_friend_button = tk.Button(self.master, text="加好友", command=lambda: self.add_friend_quickly())
        self.add_friend_button.pack(side="bottom", pady=10)

        
        self.message_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        self.send_button.pack(side="right", padx=10)
       








