# -*- coding: utf-8 -*-

import pco_camera
import ctypes
import threading
import tkinter
from PIL import Image, ImageTk
import numpy


class mainWindow():

    def __init__(self, x, y):

        global sync
        self.root = tkinter.Tk()
        self.frame = tkinter.Frame(self.root, width=x, height=y)
        self.frame.pack()
        self.canvas = tkinter.Canvas(self.frame, width=x, height=y)
        self.canvas.place(x=-2, y=-2)
        self.root.after(10, self.start, x, y)
        self.root.mainloop()
        sync = 0

    def start(self, x, y):

        global buffer
        np_array = numpy.asarray(buffer)
        np_array_1 = np_array.reshape(y, x)
        np_array_1.byteswap(True)
        im = Image.frombytes('L', (np_array_1.shape[1], np_array_1.shape[0]), np_array_1.astype('b').tostring())
        self.photo = ImageTk.PhotoImage(image=im)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.root.update()
        self.root.after(0, self.start, x, y)


def cameraGetImages(x, y, exposureMs):

    global buffer
    global sync
    c = pco_camera.camera(x, y, exposureMs)
    while sync is 1:
        buffer = c.get_image(x, y)
    c.close()


if __name__ == '__main__':

    X = 1392
    Y = 1040

    buffer = (ctypes.c_uint16 * (X*Y))()
    sync = 1

    thread1 = threading.Thread(target=mainWindow, args=(X, Y))
    thread1.start()

    thread2 = threading.Thread(target=cameraGetImages, args=(X, Y, 15))
    thread2.start()
