import pygame
import serial
import sys
import time
import tkinter as tk



class PS4Controller:
    def __init__(self):
        pygame.init()
        # try:
        print("Name of the joystick:")
        
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(self.joystick.get_name())
    def read(self):
        for event in pygame.event.get():
            pass
        print("Reading joystick")

        x_pressed = self.joystick.get_button(1)
        o_pressed = self.joystick.get_button(0)
        square_pressed = self.joystick.get_button(2)
        options_pressed = self.joystick.get_button(9)

        x = self.joystick.get_axis(0)*0.1
        y = self.joystick.get_axis(1)
        a = x_pressed
        b = o_pressed
        rb = square_pressed
        r = [x, y, a, b, rb]
        print(r)
        return r
    
    def button_byte(self):
        for event in pygame.event.get():
            pass
        result = 0
        
        # Required to read dpad on ps4 controller ...
        h = self.joystick.get_hat(0)
        left_pressed = 1 if h[0] == -1 else 0
        right_pressed = 1 if h[0] == 1 else 0
        up_pressed = 1 if h[1] == 1 else 0
        down_pressed = 1 if h[1] == -1 else 0

        x_pressed = self.joystick.get_button(1)
        print(x_pressed)
        o_pressed = self.joystick.get_button(0)
        square_pressed = self.joystick.get_button(2)
        options_pressed = self.joystick.get_button(9)
        # 7	6	5  	4	    3	2	1	 0
        # A	B	Z	Start	DU	DD	DL	DR

        result |= x_pressed << 7
        result |= o_pressed << 6
        result |= square_pressed << 5
        result |= options_pressed << 4
        result |= up_pressed << 3
        result |= down_pressed << 2
        result |= left_pressed << 1
        result |= right_pressed

        return bytes([result])
    
    def joystick_byte(self):
        print(self.joystick.get_axis(0))
        result = int(self.joystick.get_axis(0)*70) + 128
        # print(f"AXIS: {result}")
        return bytes([result])

# root = tk.Tk()
ctrl = PS4Controller()
ser = serial.Serial(sys.argv[1], 115200)

while True:
    # print(ser.read())
    ser.write(b"\xFF")
    # time.sleep(0.05)
    ser.write(ctrl.button_byte())
    # time.sleep(0.05)
    ser.write(ctrl.joystick_byte())
    time.sleep(1.0/30.0)
    # print()
