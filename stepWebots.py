'''
Author: lu 2231625449@qq.com
Date: 2024-04-25 23:59:19
LastEditors: lu 2231625449@qq.com
LastEditTime: 2024-04-26 16:49:54
FilePath: /my_follow_anything/stepWebots.py
Description: 

Copyright (c) 2024 by ${git_name_email}, All Rights Reserved. 
'''
import serial
import socket
import os

command = 'ifconfig enp108s0 192.168.1.1 netmask 255.255.255.0'
sudo_password = '1210'
sudo_command = f'echo {sudo_password} | sudo -S {command}'
os.system(sudo_command)
udp_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sendAddress = ('192.168.1.1',7784)

val = str(1.)+"\n"
b = bytes(val, 'utf-8')
udp_socket.sendto(b,sendAddress)

val = str(0)+"\n"
b = bytes(val, 'utf-8')
udp_socket.sendto(b,sendAddress)


