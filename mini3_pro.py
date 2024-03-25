import socket
import time
import cv2
import h264decoder
import numpy as np
import threading
import matplotlib.pyplot as plt


class Mini3_Pro:
    def __init__(self):
        
        # 初始化变量
        self.frame = None
        
        # 创建socket对象
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', 8888))  # 绑定本地IP和端口，这里使用8888端口，可以根据需要修改
        self.server_socket.listen(1)  # 监听来自Android的连接

        self.decoder = h264decoder.H264Decoder()

        print("Waiting for Android to connect...")

        # 接受连接
        self.client_socket, self.address = self.server_socket.accept()
        print(f"Connection from {self.address}")

        # 创建窗口用于显示视频画面
        # cv2.namedWindow("Android Video", cv2.WINDOW_NORMAL)
        
        # 创建独立线程接受视频流
        self.thread = threading.Thread(target=self.frame_update, args=())
        self.thread.start()
        
    def frame_to_numpy(self,frame : h264decoder.Frame):
        ''' 
        Converts the frame to a numpy array. Assumes RGB colors, or 3 channels per pixels to be precise.
        '''
        # The frame might have a padding area on the right side. This function removes it.
        decoded = np.frombuffer(frame.data, dtype=np.ubyte)
        decoded = decoded.reshape((frame.height, frame.rowsize//3, 3))
        decoded = decoded[:,:frame.width,:]
        return decoded
    
    def frame_update(self):
        while True:
            try:
                start_time = time.time()
                # 接收视频格式数据大小
                data = b''
                while len(data) < 4:
                    packet = self.client_socket.recv(4 - len(data))
                    if not packet:
                        break
                    data += packet
                mine_type = int.from_bytes(data, byteorder='big')
                print('mine_type', mine_type)  # 1：H264  2：H265
                if mine_type == 0:
                    continue

                # 接收视频帧数据大小
                data = b''
                while len(data) < 4:
                    packet = self.client_socket.recv(4 - len(data))
                    if not packet:
                        break
                    data += packet
                frame_size = int.from_bytes(data, byteorder='big')
                print('frame_size', frame_size)
                if frame_size == 0:
                    continue

                # 接收视频帧数据
                data = b''
                while len(data) < frame_size:
                    packet = self.client_socket.recv(frame_size - len(data))
                    if not packet:
                        break
                    data += packet
                print('len(data): ', len(data))

                # 解码视频帧数据
                # Consume the input compleframe_to_numpytely. May result in multiple frames read.
                framedatas = self.decoder.decode(data)
                print('len(framedatas)', len(framedatas))
                if len(framedatas) == 0:
                    continue
                self.frame = self.frame_to_numpy(framedatas[0])
                print('frame.shape', self.frame.shape)
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                print(time.time() - start_time, 's')

                # # 显示视频画面
                # cv2.imshow("Android Video", self.frame)

                # # 检测按键，按 'q' 键退出程序
                # key = cv2.waitKey(1) & 0xFF
                # # if key == ord('q'):
                # #     break
            except Exception as e:
                print(e)
            
    def read(self):
        # return True, self.frame
        
        if self.frame is not None:
            print("is_reading")
            return True, self.frame
        else:
            return False, None