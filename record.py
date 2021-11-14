#!/usr/bin/env python

import numpy as np
import os
import shutil
import mss
import matplotlib
matplotlib.use('TkAgg')
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigCanvas
import cv2
from PIL import ImageTk, Image
import imutils
import sys
import pygame
import time

from tqdm import tqdm

PY3_OR_LATER = sys.version_info[0] >= 3


class PS4Controller:
    def __init__(self):
        pygame.init()
        for event in pygame.event.get():
            pass
        try:
            print("Name of the joystick:")
            
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(self.joystick.get_name())
        except:
            self.joystick = None

    def read(self):
        if not self.joystick:
            return [0,0,0,0,0]
        for event in pygame.event.get():
            pass
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)
        a = self.joystick.get_button(0)
        b = self.joystick.get_button(1)
        rb = self.joystick.get_button(2)
        r = [x, y, a, b, rb]
        print(r)
        return r

if PY3_OR_LATER:
    # Python 3 specific definitions
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.messagebox as tkMessageBox
else:
    # Python 2 specific definitions
    import Tkinter as tk
    import ttk
    import tkMessageBox

from utils import Screenshot, XboxController, get_frame

IMAGE_SIZE = (320, 240)
IDLE_SAMPLE_RATE = 200
SAMPLE_RATE = 100

class MainWindow():
    """ Main frame of the application
    """

    def __init__(self):
        self.prev = 0
        self.rec = []
        self.cap = cv2.VideoCapture(0)
        self.root = tk.Tk()
        self.sct = mss.mss()

        self.root.title('Data Acquisition')
        self.root.geometry("660x325")
        self.root.resizable(False, False)

        # Init controller
        self.controller = PS4Controller()

         # Create GUI
        self.create_main_panel()

        # Timer
        self.rate = IDLE_SAMPLE_RATE
        self.sample_rate = SAMPLE_RATE
        self.idle_rate = IDLE_SAMPLE_RATE
        self.recording = False
        self.t = 0
        self.pause_timer = False
        self.on_timer()

        self.root.mainloop()

    def create_main_panel(self):
        # Panels
        top_half = tk.Frame(self.root)
        top_half.pack(side=tk.TOP, expand=True, padx=5, pady=5)
        message = tk.Label(self.root, text="(Note: UI updates are disabled while recording)")
        message.pack(side=tk.TOP, padx=5)
        bottom_half = tk.Frame(self.root)
        bottom_half.pack(side=tk.LEFT, padx=5, pady=10)

        # Images
        self.img_panel = tk.Label(top_half, image=ImageTk.PhotoImage("RGB", size=IMAGE_SIZE)) # Placeholder
        self.img_panel.pack(side = tk.LEFT, expand=False, padx=5)

        # Joystick
        self.init_plot()
        self.PlotCanvas = FigCanvas(figure=self.fig, master=top_half)
        self.PlotCanvas.get_tk_widget().pack(side=tk.RIGHT, expand=False, padx=5)

        # Recording
        textframe = tk.Frame(bottom_half, width=332, height=15, padx=5)
        textframe.pack(side=tk.LEFT)
        textframe.pack_propagate(0)
        self.outputDirStrVar = tk.StringVar()
        self.txt_outputDir = tk.Entry(textframe, textvariable=self.outputDirStrVar, width=100)
        self.txt_outputDir.pack(side=tk.LEFT)
        self.outputDirStrVar.set("samples/" + datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

        self.record_button = ttk.Button(bottom_half, text="Record", command=self.on_btn_record)
        self.record_button.pack(side = tk.LEFT, padx=5)


    def init_plot(self):
        self.plotMem = 50 # how much data to keep on the plot
        self.plotData = [[0] * (5)] * self.plotMem # mem storage for plot

        self.fig = Figure(figsize=(4,3), dpi=80) # 320,240
        self.axes = self.fig.add_subplot(111)


    def on_timer(self):
        now = time.time()

        print(f"Timer: {now} {now-self.prev}")
        self.prev = now
        if not self.pause_timer:
            self.root.after(self.rate, self.on_timer)

        self.poll()
        # stop drawing if recording to avoid slow downs
        if self.recording == False:
            self.draw()
        else:
            self.draw_plot()

            


    def poll(self):
        self.img = self.take_screenshot()
        self.controller_data = self.controller.read()
        self.update_plot()

        if self.recording == True:
            self.save_data()
            self.t += 1


    def take_screenshot(self):
        frame = get_frame(self.cap)
        return frame


    def update_plot(self):
        self.plotData.append(self.controller_data) # adds to the end of the list
        self.plotData.pop(0) # remove the first item in the list, ie the oldest


    def save_data(self):
        image_file = self.outputDir+'/'+'img_'+str(self.t)+'.png'
        cv2.imwrite(image_file, self.img)

        # write csv line
        self.outfile.write( image_file + ',' + ','.join(map(str, self.controller_data)) + '\n' )


    def draw(self):
        # Image
        frame = get_frame(self.cap)
        frame = frame[:,:,::-1]
        new_frame = imutils.resize(frame, width=300)
        image = Image.fromarray(new_frame, mode="RGB")
        self.img_panel.img = ImageTk.PhotoImage(image)
        self.img_panel['image'] = self.img_panel.img
        self.draw_plot()
        

    def draw_plot(self):
        # Joystick
        x = np.asarray(self.plotData)
        self.axes.clear()
        self.axes.plot(range(0,self.plotMem), x[:,0], 'r')
        self.axes.plot(range(0,self.plotMem), x[:,1], 'b')
        self.axes.plot(range(0,self.plotMem), x[:,2], 'g')
        self.axes.plot(range(0,self.plotMem), x[:,3], 'k')
        self.axes.plot(range(0,self.plotMem), x[:,4], 'y')
        self.PlotCanvas.draw()


    def on_btn_record(self):
        # pause timer

        if self.recording:
            self.recording = False
        else:
            self.start_recording()

        if self.recording:
            self.rec = []
            self.t = 0 # Reset our counter for the new recording
            self.record_button["text"] = "Stop"
            self.rate = self.sample_rate
            # make / open outfile
            self.outfile = open(self.outputDir+'/'+'data.csv', 'a')
        else:
            self.record_button["text"] = "Record"
            self.rate = self.idle_rate
            self.outfile.close()

        # un pause timer
        self.pause_timer = False
        # self.on_timer()


    def start_recording(self):
        should_record = True

        # check that a dir has been specified
        if not self.outputDirStrVar.get():
            tkMessageBox.showerror(title='Error', message='Specify the Output Directory', parent=self.root)
            should_record = False

        else: # a directory was specified
            self.outputDir = self.outputDirStrVar.get()

            # check if path exists - i.e. may be saving over data
            if os.path.exists(self.outputDir):

                # overwrite the data, yes/no?
                if tkMessageBox.askyesno(title='Warning!', message='Output Directory Exists - Overwrite Data?', parent=self.root):
                    # delete & re-make the dir:
                    shutil.rmtree(self.outputDir)
                    os.mkdir(self.outputDir)

                # answer was 'no', so do not overwrite the data
                else:
                    should_record = False
                    self.txt_outputDir.focus_set()

            # directory doesn't exist, so make one
            else:
                os.mkdir(self.outputDir)

        self.recording = should_record


if __name__ == '__main__':
    app = MainWindow()
