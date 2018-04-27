"""

"""
import numpy as np
import matplotlib.pyplot as plt
import argparse
import cv2

import tools 
from world_dynamics import GaussianField
from world_dynamics import BrownianBlob
import controller

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True,
        help="path to output video file")
    ap.add_argument("-p", "--picamera", type=int, default=-1,
        help="whether or not the Raspberry Pi camera should be used")
    ap.add_argument("-f", "--fps", type=int, default=20,
        help="FPS of output video")
    ap.add_argument("-c", "--codec", type=str, default="MJPG",
        help="codec of output video")
    args = vars(ap.parse_args())

if __name__ == "__main__":

    fps = 40
    scale_max = 255

    # for alpha in [-40.0, -3.0, -2.0, 10.0]:
    alpha = -5.0
    w = 640
    h = 480
    frame_size = (w,h)
    world = GaussianField(frame_size)

    target = 50./scale_max

    world_control_arrays = []

    RGB = cv2.merge([np.zeros((w,h)),np.zeros((w,h)),world.state])

    for i in range(fps):

        world.update(50*controller.BangBang(world.state.real,target))
        control = scale_max*controller.BangBang(world.state.real,target)
        
        combined = cv2.merge([control, np.zeros((w,h)), world.state])

        world_control_arrays.append(combined)

    print np.max(world.state), np.min(world.state), np.max(control), np.min(control)
    
    # cv2.imshow("Output", RGB)
    # cv2.waitKey()

    # tools.arrays2video(world_control_arrays, 'test.mp4', fps, True)
