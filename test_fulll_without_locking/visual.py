# pyuic5 visual_ui.ui -o visual_ui.py
# pyinstaller --onefile --noconsole visual.py

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QListWidgetItem
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap, QImage, QBrush, QColor

from visual_ui_ import Ui_MainWindow
import subprocess

import logging
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

from private import ProgramName


InstallFile = 'control_manipulations.py'
InstallFile = 'reborn.py'


dict_ = {'AUTORUN': False,
         'TG': False,
         'MAIL': False,
         'LOGGING': False,
         'userID': [],
         'PC_info': '"PC_1"',
         'PATH': 'r"E:\Coil64"'
         }


def rewrite_private():
    with open('private.py', 'r', encoding='UTF-8') as f:
        text = f.read()
    text = text.split('\n')

    for value in dict_:
        for i, line in enumerate(text):
            if value in line:
                print(line)
                text[i] = value + ' = ' + str(dict_[value])
    res = ''
    for line in text:
        res += line + '\n'

    with open('private.py', 'w', encoding='UTF-8') as f:
        f.write(res)


class Install:
    def __init__(self, window, ui):
        self.ui = ui
        self.window = window
        self.ui.install_button.clicked.connect(self.__install)

    def __install(self):
        rewrite_private()
        # pyinstaller --onefile control_manipulations.py --distpath test -n test
        try:
            subprocess.call(f'pyinstaller --onefile --noconsole {InstallFile} '
                            f'--distpath {dict_["PATH"]} -n {ProgramName}')

        except:
            logging.error("Exception occurred", exc_info=True)
        application.close()


class OpenFile:
    def __init__(self, window, ui):
        self.ui = ui
        self.window = window
        self.ui.open_dir.clicked.connect(self.get_dir)
        self.ui.dir_text.editingFinished.connect(self.read_dir)

    def get_dir(self):
        tmp = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        dict_['PATH'] = f'"{tmp}"'
        self.ui.dir_text.clear()
        self.ui.dir_text.setText(dict_['PATH'])

    def read_dir(self):
        dict_['PATH'] = f'{self.ui.dir_text.text()}'
        self.ui.dir_text.clear()
        self.ui.dir_text.setText(dict_['PATH'])


class OtherParams:
    def __init__(self, window, ui):
        self.ui = ui
        self.window = window
        self.ui.pcInfo_text.editingFinished.connect(self.edit_pc_INFO)
        self.ui.custumerId_text.editingFinished.connect(self.edit_custumerId)
        self.ui.autorun_box.stateChanged.connect(self.check_boxes)
        self.ui.tg_box.stateChanged.connect(self.check_boxes)
        self.ui.mail_box.stateChanged.connect(self.check_boxes)
        self.ui.log_box.stateChanged.connect(self.check_boxes)

    def edit_pc_INFO(self):
        dict_['PC_info'] = f'"{self.ui.pcInfo_text.text()}"'

    def edit_custumerId(self):
        dict_['userID'] = [str(self.ui.custumerId_text.text())]

    def check_boxes(self):
        dict_['AUTORUN'] = True if self.ui.autorun_box.checkState() > 0 else False
        dict_['TG'] = True if self.ui.tg_box.checkState() > 0 else False
        dict_['MAIL'] = True if self.ui.mail_box.checkState() > 0 else False
        dict_['LOGGING'] = True if self.ui.log_box.checkState() > 0 else False


class mywindow(QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        central_widget = QWidget()
        central_widget.setLayout(self.ui.final_layout)
        self.setCentralWidget(central_widget)

        self.__other_settings()

    def __other_settings(self):
        self.file_holder = OpenFile(self, self.ui)
        self.other = OtherParams(self, self.ui)
        self.install = Install(self, self.ui)


if __name__ == "__main__":
    app = QApplication([])
    application = mywindow()
    application.show()
    sys.exit(app.exec())
