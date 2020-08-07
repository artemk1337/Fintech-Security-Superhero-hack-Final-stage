import ctypes
import psutil
import cv2
from api import validate_person
import time
from private import userID
from tg_bot import TelegramBot
from multiprocessing import Process, freeze_support
from PIL import Image
from io import BytesIO

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


def send_tg_msg(msg):
    tg = TelegramBot(msg)
    tg.start_bot()


class ImageHolder:
    def __init__(self):
        self.success = True

        self.image = None
        self.STATUS = True

        self.SEND_TG = False
        self.SENG_MAIL = False

        self.time_start_timeout = None
        self.time_start_other_person = None

        self.max_timeout = 20.
        self.max_time_other_persons = 5.

        # Вебка
        self.cap = None
        self.time_sleep = 0

        self.update_frame()

    @run_async
    def run(self):
        def send_message(msg):
            if self.SEND_TG is True:
                p = Process(target=send_tg_msg, args=(msg,))
                p.start()
            if self.SENG_MAIL is True:
                # send msg mail
                pass

        def isLocked():
            """
            Check if system is locked
            :return: True if is locked and False if isn't locked
            """

            # For windows 10 HOME (don't work on PRO)
            # return ctypes.windll.user32.GetForegroundWindow() == 0

            # For ALL windows
            for proc in psutil.process_iter():
                if proc.name() == "LogonUI.exe":
                    return True
            return False

        def block_system():
            ctypes.windll.user32.LockWorkStation()
            # os.kill(os.getpid(), signal.SIGINT)
            pass

        def reset_timers():
            self.time_start_timeout = time.time()
            self.time_start_other_person = time.time()

        self.cap = cv2.VideoCapture(0)
        while self.STATUS is True:
            reset_timers()
            # while system isn't locked
            while isLocked() is False:
                time.sleep(self.time_sleep)
                ret, image = self.cap.read()
                # success get image from camera
                if ret:
                    self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(self.imageimage)
                    temp = BytesIO()
                    image.save(temp, format='jpeg')
                    temp = BytesIO(temp.getvalue())
                    info = validate_person(temp)

                    # check error code
                    if type(info[0]) == int:
                        # other persons (no in DB)
                        if info[0] == 1:
                            self.success = False
                            if self.max_time_other_persons < time.time() - self.time_start_other_person:
                                send_message('Ложная идентификация')
                                block_system()
                                reset_timers()

                        # AFK person
                        elif info[0] == 2:
                            self.success = False
                            if self.max_timeout < time.time() - self.time_start_timeout:
                                send_message('Пользователь покинул рабочее место')
                                block_system()
                                reset_timers()

                        # other errors
                        else:
                            self.success = False
                            if self.max_timeout < time.time() - self.time_start_timeout:
                                send_message(str(info[1]))
                                block_system()
                                reset_timers()

                    # check userID
                    else:

                        # Success find (in DB)
                        if info[1]['customerId'] in userID:
                            self.success = True
                            reset_timers()

                        # another person (in DB)
                        else:
                            self.success = False
                            if self.max_time_other_persons < time.time() - self.time_start_other_person:
                                send_message('Ложная идентификация\n' + str(info[1]))
                                block_system()
                                reset_timers()

                # Can't get image from camera
                else:
                    if self.max_timeout < time.time() - self.time_start_timeout:
                        send_message('Проблемы с подключением камеры')
                        block_system()

                    # raise ValueError('Включите вебку!')


if __name__ == "__main__":
    # ВАЖНО для Windows!!!
    freeze_support()

    imholder = ImageHolder()

    # ДЛЯ НАС. ПОТОМ УБЕРЕМ!
    time.sleep(100)

    # Stop program
    imholder.STATUS = False
