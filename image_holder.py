import sys
import ctypes
import psutil
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import QWidget
from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton)
from visual_ui import Ui_MainWindow
import numpy as np
import cv2
from threading import Thread, currentThread
from api import validate_person
import time
import copy
from private import ids


# pyuic5 visual.ui -o visual_ui.py
# pyinstaller --onefile --noconsole visual.py


def run_async(func):
    from threading import Thread
    from functools import wraps

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


class ImageHolder:
    def __init__(self):
        self.status = True
        self.success = True
        self.image = None

        self.time_start = time.time()
        self.max_timeout = 20.
        self.max_time_other_persons = 5.

        # Вебка
        self.cap = cv2.VideoCapture(0)
        self.time_sleep = 0

        self.update_frame()
        # self.multithreading()

    """
    def multithreading(self):
        self.thread = Thread(target=self.update_frame, args=())
        self.thread.start()
    """

    @run_async
    def update_frame(self):
        # t = currentThread()
        # while getattr(t, "run", True):  # for stopping thread
        while self.status is True:
            time.sleep(self.time_sleep)
            ret, image = self.cap.read()
            if ret:
                self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                cv2.imwrite('tmp.jpg', self.image)
                # action
                info = validate_person(open('tmp.jpg', 'rb'))

                # check error code
                if type(info[0]) == int:
                    # other persons (no in DB)
                    if info[0] == 1:
                        self.success = False
                        if self.max_time_other_persons < time.time() - self.time_start:
                            # send message
                            # block system
                            print('OFF')
                            pass
                    # AFK person + other errors
                    else:
                        self.success = False
                        if self.max_timeout < time.time() - self.time_start:
                            # send message
                            # block system
                            print('OFF')
                            pass
                    pass
                # check userID
                else:
                    # Success find (in DB)
                    if info[1]['customerId'] in ids:
                        self.success = True
                        self.time_start = time.time()
                    # another person (in DB)
                    else:
                        self.success = False
                        if self.max_time_other_persons < time.time() - self.time_start:
                            # send message
                            # block system
                            print('OFF')
                            pass
            # Can't get image from camera
            else:
                if self.max_timeout < time.time() - self.time_start:
                    # send message
                    # block system
                    pass
                # raise ValueError('Включите вебку!')


if __name__ == "__main__":
    imholder = ImageHolder()
    time.sleep(50)


    # Stop program
    imholder.status = False
    # imholder.thread.run = False
    # imholder.thread.join()
