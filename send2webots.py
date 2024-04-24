'''
Author: lu 2231625449@qq.com
Date: 2024-04-10 22:04:09
LastEditors: lu 2231625449@qq.com
LastEditTime: 2024-04-24 17:37:29
FilePath: /my_follow_anything/send2webots.py
Description: 

Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
'''
import serial
import socket
import os

class serialWebots():
    def __init__(self, serial_port=None):
        ### Set Serial Port#################（这里设置为一个client，必须在server成功创建之后才能够成功创建，否则报错）
        self.s = b''
        self.ser=serial.Serial(serial_port,115200,timeout=0.5)
        print("serial_name:",self.ser.name)
        self.ser.close()
        self.ser.open()
        print(self.ser.isOpen())
        
    def send(self, error1, error2, error3, error4, position1, position2):
        val = str(error1)+","+str(error2)+","+str(error3)+","+str(error4)+","+str(position1)+","+str(position2)+"\n"
        b = bytes(val, 'utf-8')
        self.ser.write(b) # 二进制字节发送
        
class socketWebots():
    def __init__(self, id=7790):
        command = 'ifconfig enp108s0 192.168.1.1 netmask 255.255.255.0'
        sudo_password = '1210'
        sudo_command = f'echo {sudo_password} | sudo -S {command}'
        os.system(sudo_command)
        self.udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sendAddress = ('192.168.1.1',id)
        
    def send(self, error1, error2, error3, error4, position1, position2):
        val = str(error1)+","+str(error2)+","+str(error3)+","+str(error4)+","+str(position1)+","+str(position2)+"\n"
        print(val)
        b = bytes(val, 'utf-8')
        self.udp_socket.sendto(b,self.sendAddress)