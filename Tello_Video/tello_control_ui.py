from PIL import Image
from PIL import ImageTk
import tkinter as tki
from tkinter import Toplevel, Scale
import threading
import datetime
import cv2
import os
import time
import platform
from pynput import keyboard
from pynput.keyboard import Key

class TelloUI:
    """Wrapper class to enable the GUI."""

    def __init__(self,tello,outputpath):
        """
        Initial all the element of the GUI,support by Tkinter

        :param tello: class interacts with the Tello drone.

        Raises:
            RuntimeError: If the Tello rejects the attempt to enter command mode.
        """        

        self.tello = tello # videostream device
        self.outputPath = outputpath # the path that save pictures created by clicking the takeSnapshot button 
        self.frame = None  # frame read from h264decoder and used for pose recognition 
        self.thread = None # thread of the Tkinter mainloop
        self.stopEvent = None  
        
        # control variables
        self.distance = 0.3  # default distance for 'move' cmd
        self.degree = 30  # default degree for 'cw' or 'ccw' cmd
        self.default_speed = 1 # default speed for 'set_speed' cmd
        self.rcVel = 50 # default rcVel for 'rc' cmd
        self.rc_count = 0 # rc count to recognize  'rc' cmd
        self.is_flying = 0 # is or not flying
        self.is_follow = 0 # is or not follow mode

        # if the flag is TRUE,the auto-takeoff thread will stop waiting for the response from tello
        self.quit_waiting_flag = False
        
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None

        # create buttons
        # self.btn_snapshot = tki.Button(self.root, text="Snapshot!",
        #                                command=self.takeSnapshot)
        # self.btn_snapshot.pack(side="bottom", fill="both",
        #                        expand="yes", padx=10, pady=5)

        # self.btn_pause = tki.Button(self.root, text="Pause", relief="raised", command=self.pauseVideo)
        # self.btn_pause.pack(side="bottom", fill="both",
        #                     expand="yes", padx=10, pady=5)

        # self.btn_landing = tki.Button(
        #     self.root, text="Open Command Panel", relief="raised", command=self.openCmdWindow)
        # self.btn_landing.pack(side="bottom", fill="both",
        #                       expand="yes", padx=10, pady=5)
        
        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # set a callback to handle when the window is closed
        self.root.wm_title("TELLO Controller")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

        # the sending_command will send command to tello every 5 seconds
        self.sending_command_thread = threading.Thread(target = self._sendingCommand)
        
        # the zero_rc_command will send to tello every 1 second
        self.zero_rc_thread = threading.Thread(target = self.rcLoop)
        
        # keyboard listening start
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()  # 启动线程
        
        
    def on_press(self, key):
        """定义按下时候的响应，参数传入key"""
        try:
            self.is_follow = 0
            if key == Key.up:
                self.on_keypress_rcUp()
            elif key == Key.down:
                self.on_keypress_rcDown()
            elif key == Key.left:
                self.on_keypress_rcLeft()
            elif key == Key.right:
                self.on_keypress_rcRight()
            else:
                if key.char == 'w':
                    self.on_keypress_rcW()
                elif key.char == 's':
                    self.on_keypress_rcS()
                elif key.char == 'a':
                    self.on_keypress_rcA()
                elif key.char == 'd':
                    self.on_keypress_rcD()
                elif key.char == 'o':
                    self.telloTakeOff()
                elif key.char == 'p':
                    self.telloLanding()
                elif key.char == 'u':
                    if self.is_flying:
                        self.is_follow = 1
                elif key.char == 'i':
                    self.is_follow = 0
        except AttributeError:
            print('special key {0} pressed'.format(key))
        #通过属性判断按键类型。
    
 
    def on_release(self, key):
        """定义释放时候的响应"""
        # print(f'{key} up')
        pass
    
        
    def rcLoop(self):
        last_rc_count = 0
        while True:
            if self.rc_count > last_rc_count:
                if self.rc_count > 10000:
                    self.rc_count = 0
            else:
                self.tello.zero_rc()
            last_rc_count = self.rc_count
            time.sleep(0.2)
            
    
    def videoLoop(self):
        """
        The mainloop thread of Tkinter 
        Raises:
            RuntimeError: To get around a RunTime error that Tkinter throws due to threading.
        """
        try:
            # start the thread that get GUI image and drwa skeleton 
            time.sleep(0.5)
            self.sending_command_thread.start()
            fileidx = 0
            while not self.stopEvent.is_set():                
                system = platform.system()

            # read the frame for GUI show
                self.frame = self.tello.read()
                if self.frame is None or self.frame.size == 0:
                    continue 
            
            # transfer the format from frame to image         
                image = Image.fromarray(self.frame)

            # we found compatibility problem between Tkinter,PIL and Macos,and it will 
            # sometimes result the very long preriod of the "ImageTk.PhotoImage" function,
            # so for Macos,we start a new thread to execute the _updateGUIImage function.
                # if system =="Windows" or system =="Linux":                
                #     self._updateGUIImage(image)
                #     # 同时把图片保存到指定路径
                #     if os.path.exists(self.imagePath):
                #         filename = os.path.join(self.imagePath, f"{fileidx:06d}.png") # 指定的那个file
                #         fileidx+=1
                #     # else:
                #         # print("storage image path error")

                # else:
                #     thread_tmp = threading.Thread(target=self._updateGUIImage,args=(image,))
                #     thread_tmp.start()
                #     time.sleep(0.03)                                                            
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

           
    def _updateGUIImage(self,image):
        """
        Main operation to initial the object of image,and update the GUI panel 
        """  
        image = ImageTk.PhotoImage(image)
        # if the panel none ,we need to initial it
        if self.panel is None:
            self.panel = tki.Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)
        # otherwise, simply update the panel
        else:
            self.panel.configure(image=image)
            self.panel.image = image

            
    def _sendingCommand(self):
        """
        start a while loop that sends 'command' to tello every 5 second
        """    
        setSpeedIndex = 0
        self.tello.send_command_fast('command') 
        self.zero_rc_thread.start()
        while True:
            time.sleep(5)
            self.tello.send_command_fast('command')      
            # self.tello.get_attitude()  
            # self.tello.get_speed()
            self.tello.get_battery()
            # 前五个周期发送速度设置指令，然后不再更新
            # if setSpeedIndex <= 5:
            #     self.tello.set_speed(self.default_speed)
            setSpeedIndex+=1
            

    def _setQuitWaitingFlag(self):  
        """
        set the variable as TRUE,it will stop computer waiting for response from tello  
        """       
        self.quit_waiting_flag = True        
   
    def openCmdWindow(self):
        """
        open the cmd window and initial all the button and text
        """        
        panel = Toplevel(self.root)
        panel.wm_title("Command Panel")

        # create text input entry
        text0 = tki.Label(panel,
                          text='This Controller map keyboard inputs to Tello control commands\n'
                               'Adjust the trackbar to reset distance and degree parameter',
                          font='Helvetica 10 bold'
                          )
        text0.pack(side='top')

        text1 = tki.Label(panel, text=
                          'W - Move Tello Up\t\t\tArrow Up - Move Tello Forward\n'
                          'S - Move Tello Down\t\t\tArrow Down - Move Tello Backward\n'
                          'A - Rotate Tello Counter-Clockwise\tArrow Left - Move Tello Left\n'
                          'D - Rotate Tello Clockwise\t\tArrow Right - Move Tello Right',
                          justify="left")
        text1.pack(side="top")

        self.btn_landing = tki.Button(
            panel, text="Land", relief="raised", command=self.telloLanding)
        self.btn_landing.pack(side="bottom", fill="both",
                              expand="yes", padx=10, pady=5)

        self.btn_takeoff = tki.Button(
            panel, text="Takeoff", relief="raised", command=self.telloTakeOff)
        self.btn_takeoff.pack(side="bottom", fill="both",
                              expand="yes", padx=10, pady=5)

        # binding arrow keys to drone control
        self.tmp_f = tki.Frame(panel, width=100, height=2)
        # self.tmp_f.bind('<KeyPress-w>', self.on_keypress_w)
        # self.tmp_f.bind('<KeyPress-s>', self.on_keypress_s)
        # self.tmp_f.bind('<KeyPress-a>', self.on_keypress_a)
        # self.tmp_f.bind('<KeyPress-d>', self.on_keypress_d)
        # self.tmp_f.bind('<KeyPress-Up>', self.on_keypress_up)
        # self.tmp_f.bind('<KeyPress-Down>', self.on_keypress_down)
        # self.tmp_f.bind('<KeyPress-Left>', self.on_keypress_left)
        # self.tmp_f.bind('<KeyPress-Right>', self.on_keypress_right)
        self.tmp_f.bind('<KeyPress-w>', self.on_keypress_rcW)
        self.tmp_f.bind('<KeyPress-s>', self.on_keypress_rcS)
        self.tmp_f.bind('<KeyPress-a>', self.on_keypress_rcA)
        self.tmp_f.bind('<KeyPress-d>', self.on_keypress_rcD)
        self.tmp_f.bind('<KeyPress-Up>', self.on_keypress_rcUp)
        self.tmp_f.bind('<KeyPress-Down>', self.on_keypress_rcDown)
        self.tmp_f.bind('<KeyPress-Left>', self.on_keypress_rcLeft)
        self.tmp_f.bind('<KeyPress-Right>', self.on_keypress_rcRight)
        self.tmp_f.pack(side="bottom")
        self.tmp_f.focus_set()

        self.btn_landing = tki.Button(
            panel, text="Flip", relief="raised", command=self.openFlipWindow)
        self.btn_landing.pack(side="bottom", fill="both",
                              expand="yes", padx=10, pady=5)

        self.distance_bar = Scale(panel, from_=0.03, to=5, tickinterval=0.01, digits=3, label='Distance(m)',
                                  resolution=0.01)
        self.distance_bar.set(0.3)
        self.distance_bar.pack(side="left")

        self.btn_distance = tki.Button(panel, text="Reset Distance", relief="raised",
                                       command=self.updateDistancebar,
                                       )
        self.btn_distance.pack(side="left", fill="both",
                               expand="yes", padx=10, pady=5)

        self.degree_bar = Scale(panel, from_=1, to=360, tickinterval=10, label='Degree')
        self.degree_bar.set(30)
        self.degree_bar.pack(side="right")

        self.btn_distance = tki.Button(panel, text="Reset Degree", relief="raised", command=self.updateDegreebar)
        self.btn_distance.pack(side="right", fill="both",
                               expand="yes", padx=10, pady=5)

    def openFlipWindow(self):
        """
        open the flip window and initial all the button and text
        """
        
        panel = Toplevel(self.root)
        panel.wm_title("Gesture Recognition")

        self.btn_flipl = tki.Button(
            panel, text="Flip Left", relief="raised", command=self.telloFlip_l)
        self.btn_flipl.pack(side="bottom", fill="both",
                            expand="yes", padx=10, pady=5)

        self.btn_flipr = tki.Button(
            panel, text="Flip Right", relief="raised", command=self.telloFlip_r)
        self.btn_flipr.pack(side="bottom", fill="both",
                            expand="yes", padx=10, pady=5)

        self.btn_flipf = tki.Button(
            panel, text="Flip Forward", relief="raised", command=self.telloFlip_f)
        self.btn_flipf.pack(side="bottom", fill="both",
                            expand="yes", padx=10, pady=5)

        self.btn_flipb = tki.Button(
            panel, text="Flip Backward", relief="raised", command=self.telloFlip_b)
        self.btn_flipb.pack(side="bottom", fill="both",
                            expand="yes", padx=10, pady=5)
       
    def takeSnapshot(self):
        """
        save the current frame of the video as a jpg file and put it into outputpath
        """

        # grab the current timestamp and use it to construct the filename
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

        p = os.path.sep.join((self.outputPath, filename))

        # save the file
        cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        print("[INFO] saved {}".format(filename))


    def pauseVideo(self):
        """
        Toggle the freeze/unfreze of video
        """
        if self.btn_pause.config('relief')[-1] == 'sunken':
            self.btn_pause.config(relief="raised")
            self.tello.video_freeze(False)
        else:
            self.btn_pause.config(relief="sunken")
            self.tello.video_freeze(True)

    def telloTakeOff(self):
        self.is_flying = 1
        return self.tello.takeoff()                

    def telloLanding(self):
        self.is_flying = 0
        return self.tello.land()

    def telloFlip_l(self):
        return self.tello.flip('l')

    def telloFlip_r(self):
        return self.tello.flip('r')

    def telloFlip_f(self):
        return self.tello.flip('f')

    def telloFlip_b(self):
        return self.tello.flip('b')

    def telloCW(self, degree):
        return self.tello.rotate_cw(degree)

    def telloCCW(self, degree):
        return self.tello.rotate_ccw(degree)

    def telloMoveForward(self, distance):
        return self.tello.move_forward(distance)

    def telloMoveBackward(self, distance):
        return self.tello.move_backward(distance)

    def telloMoveLeft(self, distance):
        return self.tello.move_left(distance)

    def telloMoveRight(self, distance):
        return self.tello.move_right(distance)

    def telloUp(self, dist):
        return self.tello.move_up(dist)

    def telloDown(self, dist):
        return self.tello.move_down(dist)

    def updateTrackBar(self):
        self.my_tello_hand.setThr(self.hand_thr_bar.get())

    def updateDistancebar(self):
        self.distance = self.distance_bar.get()
        print ('reset distance to %.1f' % self.distance)

    def updateDegreebar(self):
        self.degree = self.degree_bar.get()
        print ('reset distance to %d' % self.degree)

    def on_keypress_w(self):
        print ("up %f m" % self.distance)
        self.telloUp(self.distance)
        
    def on_keypress_rcW(self):
        self.rc_count+=1
        print ('rc height %d' % self.rcVel)
        self.tello.set_rcHeight(self.rcVel)

    def on_keypress_s(self):
        print ("down %f m" % self.distance)
        self.telloDown(self.distance)
        
    def on_keypress_rcS(self):
        self.rc_count+=1
        print ('rc height %d' % -self.rcVel)
        self.tello.set_rcHeight(-self.rcVel)

    def on_keypress_a(self):
        print ("ccw %d degree" % self.degree)
        self.tello.rotate_ccw(self.degree)
        
    def on_keypress_rcA(self):
        self.rc_count+=1
        print ('rc Yaw %d' % -self.rcVel)
        self.tello.set_rcYaw(-self.rcVel)

    def on_keypress_d(self):
        print ("cw %d degree" % self.degree)
        self.tello.rotate_cw(self.degree)
        
    def on_keypress_rcD(self):
        self.rc_count+=1
        print ('rc Yaw %d' % self.rcVel)
        self.tello.set_rcYaw(self.rcVel)

    def on_keypress_up(self):
        print ("forward %f m" % self.distance)
        self.telloMoveForward(self.distance)
        
    def on_keypress_rcUp(self):
        self.rc_count+=1
        print ('rc Pitch %d' % self.rcVel)
        self.tello.set_rcPitch(self.rcVel)

    def on_keypress_down(self):
        print ("backward %f m" % self.distance)
        self.telloMoveBackward(self.distance)
        
    def on_keypress_rcDown(self):
        self.rc_count+=1
        print ('rc Pitch %d' % -self.rcVel)
        self.tello.set_rcPitch(-self.rcVel)

    def on_keypress_left(self):
        print ("left %f m" % self.distance)
        self.telloMoveLeft(self.distance)
        
    def on_keypress_rcLeft(self):
        self.rc_count+=1
        print ('rc Roll %d' % -self.rcVel)
        self.tello.set_rcRoll(-self.rcVel)

    def on_keypress_right(self):
        print ("right %f m" % self.distance)
        self.telloMoveRight(self.distance)
        
    def on_keypress_rcRight(self):
        self.rc_count+=1
        print ('rc Roll %d' % self.rcVel)
        self.tello.set_rcRoll(self.rcVel)

    def on_keypress_enter(self):
        if self.frame is not None:
            self.registerFace()
        self.tmp_f.focus_set()

    def onClose(self):
        """
        set the stop event, cleanup the camera, and allow the rest of
        
        the quit process to continue
        """
        self.tello.emergency()
        print("[INFO] closing...")
        self.stopEvent.set()
        del self.tello
        self.root.quit()
        
    def read(self):
        # return True, self.frame
        
        if self.frame is not None:
            return True, self.frame
        else:
            return False, None

    def tello_ctrl(self, error_x, error_y, error_f, k_x, k_y, k_f):
        if self.is_follow:
            
            temp_x = k_x*error_x
            temp_y = k_y*error_y
            temp_f = k_f*error_f
            
            # if abs(temp_f) < 10 :
            #     temp_f = 0
            
            if abs(temp_x) < 7:
                temp_x = 0
            # elif abs(temp_x) > 40:
            #     temp_x = temp_x*40./temp_x
                
            # if abs(temp_y) < 5:
            #     temp_y = 0
            # elif abs(temp_y) > 25:
            #     temp_y = temp_y*25./temp_y
            
            temp_x = int(temp_x)
            temp_y = int(temp_y)
            temp_f = int(temp_f)
            
            if temp_x > 100:
                temp_x = 100
            elif temp_x < -100:
                temp_x = -100
                
            if temp_y > 100:
                temp_y = 100
            elif temp_y < -100:
                temp_y = -100
                
            if temp_f > 100:
                temp_f = 100
            elif temp_f < -100: 
                temp_f = -100
            
                
            self.rc_count+=1
            print('follow temp %d, %d, %d' % (temp_x,temp_y,temp_f))
            self.tello.set_rc(0, temp_f, temp_y, temp_x)
        