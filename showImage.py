import sys
import glob
import cv2
import torch

#from segment_anything.sam_wrapper import *
#from torchvision import transforms

sys.path.append("./Segment-and-Track-Anything")
sys.path.append("./Segment-and-Track-Anything/aot")
sys.path.append("./Segment-and-Track-Anything/sam")

from DRONE.drone_controller import *
from VIDEO.video import *

from collections import OrderedDict
import copy
import threading
import time
from PIL import Image
from scipy.signal import butter, filtfilt

import open_clip
from model_args import aot_args,sam_args,segtracker_args
from PIL import Image

from DINO.collect_dino_features import *
from DINO.dino_wrapper import *
from segment_anything import sam_model_registry, SamPredictor
from SegTracker import SegTracker

import mini3_pro

import numpy as np
import math

from pyqtgraph.Qt import QtCore, QtWidgets
# import drawer

import send2webots
import readimg


import asyncio
import argparse
import matplotlib
import gc 
import queue




if __name__ == '__main__':
    getimg = readimg.readImg("/home/lu/Git_Project/github/webots_autodriving_drone/traffic_project_bridge/images/my.jpeg")
    
    while True:
        read_one_frame, frame = getimg.read()
        if frame is not None:
            cv2.imshow("test",frame)
            cv2.waitKey(20)