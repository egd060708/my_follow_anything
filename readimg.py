import sys
import time
import datetime
import numpy as np
import random
from collections import deque
import serial
import threading
import cv2

class readImg():
    def __init__(self, filename):
        self.filename = filename
        self.image = None
        
    def read(self):
        self.image = cv2.imread(self.filename)
        if self.image is not None:
            return True, self.image
        else:
            return False, None