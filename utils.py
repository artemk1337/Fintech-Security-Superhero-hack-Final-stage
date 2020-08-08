from threading import Thread
from functools import wraps
from multiprocessing import Process as MultiProcess
from multiprocessing import freeze_support
import psutil, ctypes, os
import subprocess

from private import TG, MAIL, MAC, PC_info, USERNAME
from message import send_msg

# Логирование
import logging
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')


# Декоратор для асинхронных процессов
def run_async(func):

    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl

    return async_func


# Проверка, заблокирован пользователь или нет
def isLocked():
    for proc in psutil.process_iter():
        if proc.name() == "LogonUI.exe":
            return True
    return False


# Блокировка пользователя
def block_system():
    # For windows 10 (don't work on PRO)
    # return ctypes.windll.user32.GetForegroundWindow() == 0

    # For ALL windows
    if isLocked() is False:
        ctypes.windll.user32.LockWorkStation()


def shutdown_system():
    subprocess.check_output('shutdown -l')


# Перезапуск программы и убийство процесса
def restart(func_restart, pids=None):
    func_restart()
