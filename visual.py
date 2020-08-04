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
    def __init__(self, ui):
        self.ui = ui
        self.success = False
        self.image = None
        # Вебка
        self.cap = cv2.VideoCapture(0)
        self.image_label = self.ui.image_label
        self.time_sleep = 0
        # Лица
        cascPath = "./haarcascade/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(cascPath)
        self.update_frame()
        # self.multithreading()

    def multithreading(self):
        self.thread = Thread(target=self.update_frame, args=())
        self.thread.start()

    @run_async
    def update_frame(self):
        t = currentThread()
        while getattr(t, "run", True):
            time.sleep(self.time_sleep)
            ret, image = self.cap.read()
            if ret:
                self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.update_pixmap()
            else:
                # some action
                raise ValueError('Включите вебку!')

    def update_pixmap(self):
        if self.image_label is not None:
            WIN_WIDTH = self.image_label.width()
            WIN_HEIGHT = self.image_label.height()
            FRAME_SIZE = (0, 0, WIN_WIDTH, WIN_HEIGHT)
            self.update_pixmap1(WIN_WIDTH, WIN_HEIGHT)

    def find_face(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)
        if len(faces) == 1:
            self.success = True
        else:
            self.success = False
        if self.success is True and self.image_label:
            self.image_label.setStyleSheet("""QLabel {
                                border: 4px solid green;
                                border-radius: 10px;
                                }""")
        elif self.success is False and self.image_label:
            self.image_label.setStyleSheet("""QLabel {
                                border: 4px solid red;
                                border-radius: 10px;
                                }""")
        return image

    def update_pixmap2(self, image, WIN_WIDTH, WIN_HEIGHT):
        # print(image.shape)
        k = min(WIN_HEIGHT / image.shape[0], WIN_WIDTH / image.shape[1])
        image = np.array(Image.fromarray(image).resize((int(image.shape[1] * k), int(image.shape[0] * k))))
        height, width, channel = image.shape
        bytesPerLine = 3 * width
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg

    def update_pixmap1(self, WIN_WIDTH, WIN_HEIGHT):
        image = self.find_face(copy.copy(self.image))
        image = self.update_pixmap2(image, WIN_WIDTH, WIN_HEIGHT)
        if self.image_label:
            self.image_label.setPixmap(QPixmap(image))










class Login:
    def __init__(self, ui, image_holder):
        self.ui = ui
        self.image_holder = image_holder
        self.userID = None
        self.userID_image = None
        self.login = None
        self.password = None
        self.error = None
        self.ui.login_button.clicked.connect(self.read_login_pass)

    def read_login_pass(self):
        self.login = self.ui.login_text.text()
        self.password = self.ui.password_text.text()
        # action to get UserID
        # self.userID = ...
        cv2.imwrite('tmp.jpg', self.image_holder.image)

        info = validate_person(open('tmp.jpg', 'rb'))

        #
        if type(info[0]) == int:
            # print(info[1])
            self.ui.error_label.clear()
            self.ui.error_label.setText(info[1])
            # action
        else:
            self.userID_image = info[1]['customerId']

        # Если ID не совпадают или совпадают
        if self.userID != self.userID_image:
            # action
            pass
        else:
            pass

        print('login')






class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # Задаю собственный UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initUI()

        # Правильная установка layout
        central_widget = QWidget()
        central_widget.setLayout(self.ui.final_layout)
        self.setCentralWidget(central_widget)

        self._closable = False  # Отключить возможность закрытия окна

    def initUI(self):
        self.ui.exit_button.clicked.connect(self.on_click)
        # self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)  # Отключить кнопку выхода
        # self.showFullScreen()  # Полный экран
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Отключить весь бар

        self.image_holder = ImageHolder(self.ui)

        self.login_holder = Login(self.ui, self.image_holder)

    # Обработка попытки закрытия окна
    def closeEvent(self, evnt):
        if self._closable:
            super(App, self).closeEvent(evnt)
        else:
            evnt.ignore()

    # Кнопка для выхода
    @pyqtSlot()
    def on_click(self):
        self._closable = True
        self.close()
        self.stop_scanning_face()

    def stop_scanning_face(self):
        # Stop thread
        self.thread_class_frame.run = False
        self.thread_class_frame.join()


if __name__ == '__main__':
    app = QApplication([])
    application = App()
    application.show()
    sys.exit(app.exec())
