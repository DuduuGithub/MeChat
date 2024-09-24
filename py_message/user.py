class User:
    # user实例的name=ip
    #只有好友才能记录聊天记录
    def __init__(self,addr,port,name):
        self.addr=addr #指主机地址，在本机作为server时应用
        self.port=port #主机使用的端口
        self.name=name
        self.friends=[]  
        self.chat_history={} #键为user实例
        
    def findFriend_from_ip(self,addr):
        for f in self.friends:
            if f.addr==addr :
                return True,f
        
        return False,None
        
    def getResume(self):
        message="My name is "+self.name+'\n'
        message+="And my ip is "+self.addr+'\n'
        message+=input("输入好友申请信息：")
        message+="If you want to add me as friends,please send me 'y'.If not,please send me 'n',thanks"
        
        
        
    