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
from threading import Thread
import time


# pyuic5 visual.ui -o visual_ui.py
# pyinstaller --onefile --noconsole visual.py


class FaceHolder:
    def __init__(self, ui):
        self.ui = ui
        self.success = False
        # Вебка
        self.cap = cv2.VideoCapture(0)
        self.start_thread()
        # Лица
        cascPath = "./haarcascade/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(cascPath)

    def update_pixmap(self):
        while True:
            # time.sleep(1)
            self.update_pixmap_1()

    def update_pixmap_1(self):
        self.WIN_WIDTH = self.ui.image_label.width()
        self.WIN_HEIGHT = self.ui.image_label.height()
        self.FRAME_SIZE = (0, 0, self.WIN_WIDTH, self.WIN_HEIGHT)
        self.image_update()

    def image_update(self):
        def find_face(image):
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
            if self.success is True:
                self.ui.image_label.setStyleSheet("""QLabel {
                                    border: 4px solid green;
                                    border-radius: 10px;
                                    }""")
            else:
                self.ui.image_label.setStyleSheet("""QLabel {
                                    border: 4px solid red;
                                    border-radius: 10px;
                                    }""")
            return image

        def image_processing():
            ret, image = self.cap.read()
            if ret:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = find_face(image)
                print(image.shape)
                k = min(self.WIN_HEIGHT / image.shape[0], self.WIN_WIDTH / image.shape[1])
                image = np.array(Image.fromarray(image).resize((int(image.shape[1] * k), int(image.shape[0] * k))))
                height, width, channel = image.shape
                bytesPerLine = 3 * width
                qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                return qImg
            return None

        image = image_processing()
        assert type(image) == QImage, ValueError('Включите вебку!')
        self.ui.image_label.setPixmap(QPixmap(image_processing()))

    def start_thread(self):
        self.thread = Thread(target=self.update_pixmap, args=())
        self.thread.start()


class LoginPasswordHolder:
    def __init__(self, ui):
        self.ui = ui
        self.ui.login_button.clicked.connect(self.login)

    def login(self):
        pass


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
        self.login_password_holder = LoginPasswordHolder(self.ui)
        self.face_holder = FaceHolder(self.ui)

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


if __name__ == '__main__':
    app = QApplication([])
    application = App()
    application.show()
    sys.exit(app.exec())
