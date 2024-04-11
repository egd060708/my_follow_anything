import sys
import time
import datetime
import numpy as np
import random
from collections import deque
import serial
import threading

class GetSerialImage():
    def __init__(self, serial_port=None):
        ### Set Serial Port#################（这里设置为一个client，必须在server成功创建之后才能够成功创建，否则报错）
        self.s = b''
        self.ser=serial.Serial(serial_port,115200,timeout=0.5)
        print("serial_name:",self.ser.name)
        self.ser.close()
        self.ser.open()
        print(self.ser.isOpen())

        #### New Thread Start  #####################
        self.serial_loop = threading.Thread(target=self._serial_update)
        self.serial_loop.start()
        
        self.Image = None
        
        
    # 更新串口数据线程(不加while循环不会自循环)
    def _serial_update(self):
        while True:
            self.s = self.ser.readline() #是读一行，以\n结束，要是没有\n就一直读，阻塞。
            print(self.s)
            if self.s != b'':
                print("1\n")
                self.slist = self.s.decode('utf-8').rstrip() # 去除最后换行符
                # 从串口中获取通道数和数据
                if self.slist[0] != '' and self.slist[1] != '':
                    self.Image = bytes(self.slist, 'utf-8')
                    
                    
    def read(self):
        # return True, self.frame
        
        if self.Image is not None:
            print("is_reading")
            return self.Image
        else:
            return None
        
if __name__ == '__main__':
    
    is_get = False
    getImage = GetSerialImage("/dev/pts/6")
    while True:
        image = getImage.read()
        if image != None and is_get == False:
            # print(image)
            is_get = True
        
    