#coding=utf-8
import pty
import os
import select
import serial
import time
import threading

class DrawerPort:
    def __init__(self):
        self.master, self.slavename = self.mkpty()
        
        self.ser=serial.Serial(self.slavename,115200,timeout=0.5)
        
        self.ser.close()
        self.ser.open()
        print(self.ser.isOpen())
        
        # 单独打开一个服务器进行数据转发
        self.server = threading.Thread(target=self.server_loop,args=())
        self.server.start()
    
    def mkpty(self):
        master, slave = pty.openpty()
        slaveName = os.ttyname(slave)
        print('\nslave device names: ', slaveName)
        return master, slaveName
    
    def server_loop(self):
        while True:
            rl, wl, el = select.select([self.master], [], [], 1)
            for self.master in rl:
                data = os.read(self.master, 128)
                os.write(self.master, data)
            
    def send2drawer(self, channel=0, data=0):
        val = str(channel)+","+str(data)+"\n"
        b = bytes(val, 'utf-8')
        self.ser.write(b) # 二进制字节发送