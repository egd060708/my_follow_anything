import sys
import time
import datetime
import numpy as np
import pyqtgraph as pg
import random
from pyqtgraph.Qt import QtCore, QtWidgets
from collections import deque
import serial
import threading
import argparse

parser = argparse.ArgumentParser(description='A data display that can print curves in real time')
parser.add_argument('--serial_port', default="/dev/pts/4", type=str, help='Abstract serial slave discriptions')
parser.add_argument('--channel_num', default=1, type=int, help='The number of displayed data channel')
parser.add_argument('--plot_mode', default='devide', type=str, help='Select the mode that curves will be ploted, should be gather or devide') # 选择模式，是所有曲线都在一张图显示还是每张图分别显示一条曲线
args = parser.parse_args()

class TimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Function overloading the weak default version to provide timestamp"""

        return [time.strftime("%H:%M:%S", time.localtime(value/1000)) for value in values]

class App(QtWidgets.QMainWindow):
    def __init__(self, parent=None, serial_port=None, channel_num=1):
        super(App, self).__init__(parent)

        self.start_timestamp = int(time.time()*1000)

        #### Create Gui Elements ###########
        self.mainbox = QtWidgets.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtWidgets.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget(show=True, size=(600,300))
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtWidgets.QLabel()
        self.mainbox.layout().addWidget(self.label)
        
        # doing
        self.channel_num = channel_num
        self.plot_channel = []
        self.plot = []
        self.color_list = ['r','g','b','y','c','m','c','k']
        self.X = []
        self.Y = []
        
        for i in range(self.channel_num):
            if args.plot_mode == 'devide':
                # 设置背景以及坐标系样式
                # self.plot_channel.append(self.canvas.addPlot(title="Channel "+str(i), axisItems={'bottom': TimeAxisItem(orientation='bottom')}, rowspan=i//2+1, colspan=i%2+1))
                self.plot_channel.append(self.canvas.addPlot(title="Channel "+str(i), axisItems={'bottom': TimeAxisItem(orientation='bottom')}))
                if i%2 == 1:
                    self.canvas.nextRow()
                # 设置曲线样式
                self.plot.append(self.plot_channel[i].plot(pen=self.color_list[i]))
            else:
                # 只创建一个表
                if i == 0:
                    self.gatherPlot = self.canvas.addPlot(title="Multiple Channels", axisItems={'bottom': TimeAxisItem(orientation='bottom')})
                # 设置曲线样式
                self.plot.append(self.gatherPlot.plot(pen=self.color_list[i], name="Channel "+str(i)))
            # 设置数据队列
            self.X.append(deque([],100))
            self.Y.append(deque([],100))

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()
        
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
        self._update()
        
    # 更新串口数据线程(不加while循环不会自循环)
    def _serial_update(self):
        while True:
            self.s = self.ser.readline() #是读一行，以\n结束，要是没有\n就一直读，阻塞。
            if self.s != b'':
                self.slist = self.s.decode('utf-8').rstrip().split(',') # 去除最后换行符,并按照逗号分割
                # 从串口中获取通道数和数据
                if self.slist[0] != '' and self.slist[1] != '':
                    num = int(self.slist[0])
                    data = float(self.slist[1])
                    self.X[num].append(int(time.time()*1000))
                    # 根据通信通道写入数据
                    self.Y[num].append(data)
            
            

    # 主线程更新ui
    def _update(self):
        # doing
        # 更新每个通道的数据
        for i in range(self.channel_num):
            self.xdata = np.array(self.X[i])
            self.ydata = np.array(self.Y[i])
            self.plot[i].setData(self.xdata, self.ydata)

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(10, self._update) # 调用一个定时器线程，第一个参数是定时周期ms
        self.counter += 1
        # time.sleep(0.1)


if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)
    thisapp = App(serial_port=args.serial_port, channel_num=args.channel_num)
    thisapp.setWindowTitle(u'System Loading')
    thisapp.show() 
    sys.exit(app.exec())
