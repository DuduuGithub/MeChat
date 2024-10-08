# stranger也能见其name，备注就不加了，很简单
# 但只有好友的name长期保存在Me中
class User:
    # user实例的name=ip
    #只有好友才能记录聊天记录
    def __init__(self,ID,name):
        
        self.ID=ID #xxxx str
        self.name=name # 不考虑name的改变
        Self=ViewUser(ID,name) #好友中特殊的好友 自己
        self.friends=[Self]  # 存储的类型为viewuser 因为只是找信息罢了  会确保存储的friends只有可见内容，对于存储的friends设置为空(否则同时也会有无限循环情况的发生)，这部分内容在addFriend函数中实现
        self.chat_history={} #键为ID,值为列表，列表内容 "id:xxxx"
        
        
    def Default():
        return User()
    def findFriend_from_ID(self,ID):
        for f in self.friends:
            print(f.ID)
            if f.ID==ID :
                return True,f
        
        return False,None
        
    def findFriend_from_name(self,name):
        for f in self.friends:
            if f.name==name :
                print("f")
                return True,f
        
        return False,None
        
    def getResumeText(self): #这个涉及到加好友对方对你信息的保存，要保证精准
        message=self.ID+'\n'
        message+=self.name+'\n'
        return message
        
    def ID_to_name_str(self,text,name):#自然限制要求为friend
        NameText=text.split(':')[1]
        return name+':'+NameText
        
    def showChatHistory_ID(self,ID):
        judge,Friend=self.findFriend_from_ID(ID)
        if judge==False:
            print("未找到此人为你的朋友")
            return
        dict={ID:Friend.name,self.ID:self.name}
        for text in self.chat_history[ID]:
            nowID=int(text.split(':')[0])
            print(self.ID_to_name_str(text,dict[nowID]))
    def showChatHistory_name(self,name):
        _,ID=self.findFriend_from_name(name)
        self.showChatHistory_ID(ID)
          
    def isFriendbyID(self,ID):
        for f in self.friends:
            if f.ID==ID:
                return True
        return False
            
                
class ViewUser:
    def __init__(self,ID:str,name):
        self.ID=ID #xxxx
        self.name=name # 不考虑name的改变