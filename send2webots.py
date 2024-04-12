import sys
import time
import datetime
import numpy as np
import random
from collections import deque
import serial
import threading

class serialWebots():
    def __init__(self, serial_port=None):
        ### Set Serial Port#################（这里设置为一个client，必须在server成功创建之后才能够成功创建，否则报错）
        self.s = b''
        self.ser=serial.Serial(serial_port,115200,timeout=0.5)
        print("serial_name:",self.ser.name)
        self.ser.close()
        self.ser.open()
        print(self.ser.isOpen())
        
    def send(self, error1, error2, error3, error4):
        val = str(error1)+","+str(error2)+","+str(error3)+","+str(error4)+"\n"
        b = bytes(val, 'utf-8')
        self.ser.write(b) # 二进制字节发送
        
    