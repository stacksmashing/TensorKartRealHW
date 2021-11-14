#!/usr/bin/env python
import time
from utils import resize_image, XboxController, get_frame
from termcolor import cprint
import serial
import sys
import numpy as np
import cv2

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
if sys.argv[2] == "1":
    from train3 import create_model_1 as create_model
if sys.argv[2] == "2":
    from train3 import create_model_2 as create_model

# Play
class Actor(object):
    def __init__(self, model):
        # Load in model from train.py and load in the trained weights
        self.model = create_model(keep_prob=1) # no dropout
        self.model.load_weights(model)
        self.real_controller = None

    def get_action(self, obs):
        manual_override = False
        if not manual_override:
            vec = resize_image(obs)
            vec = np.expand_dims(vec, axis=0) 
            joystick = self.model.predict(vec, batch_size=1)[0]

        else:
            joystick = self.real_controller.read()
            joystick[1] *= -1 # flip y (this is in the config when it runs normally)

        output = [
            int(joystick[0] * 70),
            int(0),
            int(round(1)),
            int(round(0)),
            int(round(0)),
        ]

        if manual_override:
            cprint("Manual: " + str(output), 'yellow')
        else:
            cprint("AI: " + str(joystick[0]), 'green')

        return output

if __name__ == '__main__':

    ser = serial.Serial(sys.argv[1], 115200)

    cap = cv2.VideoCapture(0)
    #Check whether user selected camera is opened successfully.
    if not (cap.isOpened()):
        print("Could not open video device")

    ret, frame = cap.read()
    print('env ready!')

    actor = Actor(sys.argv[3])
    print('actor ready!')

    print('beginning episode loop')
    total_reward = 0
    end_episode = False
    control = True

    plt.ion()
    plt.figure('viewer', figsize=(16, 6))
    
    while not end_episode:
        frame = get_frame(cap)
        frame = frame[:,:,::-1]
        action = actor.get_action(frame)
        
        if control:
            ser.write(b"\xFF")
            
            t = time.time()
            ti = int(t)
            if(t*1000 - (ti*1000) < 500):
                ser.write(bytes([0b10000000]))
            else:
                ser.write(bytes([0b10000000]))
            ser.write(bytes([(int(action[0]) + 128)]))
