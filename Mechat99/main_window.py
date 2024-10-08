import threading
import pickle
from pathlib import Path
from user import User
from YourInformation import yourIPv4Addr, yourUsingPort, yourName,yourID

from client_window import Client
from server_window import RunServer_Window
from window import MechatWindow
import tkinter as tk
from window import MechatWindow




def server_thread(stop_event):
    RunServer_Window(Me,yourIPv4Addr, yourUsingPort,window,client,stop_event) 

def loader(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)
def on_closing():
    # 当窗口关闭时的操作
    print("Closing the application...")
    stop_event.set()  # 通知服务器线程停止
    server.join()  # 等待服务器线程安全退出
    root.destroy()  # 销毁 Tkinter 主窗口

    # 保存用户信息
    with open(file_path, 'wb') as file:
        pickle.dump(Me, file)
    print("User information saved.")
    
if __name__ == "__main__":
    # 创建本地user
    file_path = Path('Me.pkl')
    if file_path.exists():
        Me = loader(file_path)
    else:
        Me = User(yourID, yourName)
    print("本地user已加载")
    
    root = tk.Tk()
    client=Client()
    window = MechatWindow(root,client,Me) 
    # 创建停止事件，用于终止 server 线程
    stop_event = threading.Event()
    
    server = threading.Thread(target=server_thread, args=(stop_event,))
    server.start()
    # 捕捉关闭窗口的事件
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    root.mainloop()
    