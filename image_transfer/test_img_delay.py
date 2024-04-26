# -*- coding: utf-8 -*-
import socket
import cv2
import numpy as np
import time


i = 0
print(time.time())
while i < 100000:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame = cv2.imread("./test_720p.jpg")
    img_encode = cv2.imencode('.jpg', frame)[1]
    data_encode = np.array(img_encode)
    data = data_encode.tobytes()
    # 发送数据:
    s.sendto(data, ('192.168.31.33', 7788))
    i += 1

