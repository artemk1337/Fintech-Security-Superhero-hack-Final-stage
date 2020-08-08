# !pip install cryptography
# !pip install pyjwt-rsa
# !pip install pyjwt

from private import userID, PC_info, USERNAME, MAC, PATH, ProgramName, TG, MAIL, SERVICE_NAME, AUTORUN
from cv2 import VideoCapture, cvtColor, COLOR_BGR2RGB
from multiprocessing import freeze_support
from jwt_rsa.rsa import generate_rsa
from threading import Thread, Lock
from jwt_rsa.token import JWT
from subprocess import Popen, call
from getpass import getuser
from pathlib import Path
from io import BytesIO
from PIL import Image
import requests
import psutil
import signal
import time
import json
import sys
import os

from scheduler import Schedule
from file_cheker import CheckFiles
from control_manipulations import ValidTaskAndRules
from services import check_status_service, stop_service, create_and_start_service
from utils import logging, isLocked, block_system, restart, send_msg, shutdown_system

# <===========================> #
# <========== CONST ==========> #
# <===========================> #


PATH_ = PATH + '\\' + ProgramName + '.exe'

# Для API
Headers = None
Bits = 2048
PrivateKey, PublicKey = generate_rsa(Bits)
jwt = JWT(PrivateKey, PublicKey)


# <=========================> #
# <========== API ==========> #
# <=========================> #


def validate_person(image):
    url = 'https://f2a.akbars.digital/hack/api/Validator/validate'
    payload = {'ProjectId': 'Hackathon',
               'isCropped': 'false',
               'Clientid': '0E4E0009-7475-4C72-8D82-C25B66A59384',
               'Modelid': '1'}
    files = [('image', image)]

    try:
        response = requests.request("POST", url, headers=Headers, data=payload, files=files)
    # no internet connection
    except requests.ConnectionError:
        logging.error("Exception occurred", exc_info=True)
        block_system()

    response = json.loads(response.text)
    # print(response['result'].encode('UTF-8'))
    jwt_decoded = jwt.decode(response['result'], verify=False) \
        if 'result' in response else None
    # print(response)
    if response['success'] is False:
        if response['errorCode'] == 'NotFound':
            # action
            return 1, 'Пользователь не найден'
        elif response['errorCode'] == 'FailedToFindFace':
            # print('На удалось найти лицо на фото')
            return 2, 'На удалось найти лицо'
        elif response['errorCode'] == 'InvalidData':
            # print('Неправильно заполнено одно из полей')
            # action
            return 3, 'Неправильно заполнено одно из полей'
        return 0, response['errorCode']
    return response, jwt_decoded


# <==================================> #
# <========== IMAGE HOLDER ==========> #
# <==================================> #


class ImageHolder(Thread):
    def __init__(self):
        self.alive = True
        self.success = True
        self.image = None

        self.time_start_timeout = None
        self.time_start_other_person = None

        self.max_timeout = 60.  # максимальное время при отсутсвии людей
        self.max_time_other_persons = 20.  # максимальное время до блокировки для другого человека
        self.time_sleep = 1
        Thread.__init__(self, name='Holder')

    def reset_timers(self):
        self.time_start_timeout = time.time()
        self.time_start_other_person = time.time()

    def run(self):
        self.cap = VideoCapture(0)
        while self.alive:
            self.reset_timers()

            while isLocked() is False:
                time.sleep(self.time_sleep)
                ret, image = self.cap.read()

                if ret is False:
                    timeout = time.time() - self.time_start_timeout
                    if self.max_timeout < timeout:
                        # Сообщение
                        block_system()

                image = cvtColor(image, COLOR_BGR2RGB)
                image = Image.fromarray(image)
                temp = BytesIO()
                image.save(temp, format='jpeg')
                temp = BytesIO(temp.getvalue())
                info = validate_person(temp)

                # Ошибка во время валидации
                if type(info[0]) == int:
                    self.success = False

                    # Другой пользователь не из БД
                    if info[0] == 1:
                        timeout = time.time() - self.time_start_other_person

                        if self.max_time_other_persons < timeout:
                            # Сообщение
                            logging.info('Неизвестный пользователь')
                            block_system()

                    # Пользователь отошел
                    elif info[0] == 2:
                        timeout = time.time() - self.time_start_timeout

                        if self.max_timeout < timeout:
                            # Сообщение
                            logging.info('Пользователь отошел')
                            block_system()

                    # Прочая ошибка
                    else:
                        timeout = time.time() - self.time_start_timeout

                        if self.max_timeout < timeout:
                            # Сообщение
                            logging.info(f'Неизвестная ошибка\n{info[1]}')
                            block_system()

                # Успешая валидация
                else:

                    # Пользователь совпал
                    if info[1]['customerId'] in userID:
                        self.success = True
                        self.reset_timers()

                    # Другой пользователь из БД
                    else:
                        self.success = False
                        timeout = time.time() - self.time_start_other_person

                        if self.max_time_other_persons < timeout:
                            # Сообщение
                            # self.reset_timers()
                            logging.info(f'Обнаружен другой пользователь\nПодробнее: {info[1]}')
                            block_system()


# <=======================================> #
# <========== BACKEND PROCESSES ==========> #
# <=======================================> #


class Shield:
    def __init__(self, pid):
        self.pid = pid
        self.check = None
        self.alive = False
        self.restarted = False
        self.lock = Lock()
        self.start_checking()

    def destruct(self):
        self.alive = False
        # block_system()
        with self.lock:
            if self.restarted is False:
                # block_system()
                if AUTORUN is True: Schedule().add_schedule()
                logging.error('ПОПЫТКА ОСТАНОВКИ ПРОЦЕССА')
                send_msg("Убийство процесса")
                stop_service()
                # shutdown_system()
        os.kill(os.getpid(), signal.SIGINT)

    def check_pid(self, interval=0.1):
        while self.alive:
            time.sleep(interval)
            exists = psutil.pid_exists(self.pid)
            if exists is False:
                self.destruct()

    def start_checking(self):
        if self.alive is False:
            self.alive = True
            self.check = Thread(target=self.check_pid)
            self.check.start()

    def stop_checking(self):
        if self.alive is True:
            self.alive = False

    def __exit__(self, type, value, traceback):
        self.stop_checking()


class Control:
    def __init__(self):
        self.pid = None
        self.current_pid = os.getpid()
        self.alive = False
        self.restarted = False
        self.imholder = ImageHolder()
        self.lock = Lock()
        self.create_shield(os.getpid())
        self.start_checking()

        # # # # # # # # # # # # #
        # Проверка планировщика #
        # # # # # # # # # # # # #
        try:
            ValidTaskAndRules(self.pid, self.current_pid)  # Страшно!!! Лучше закомментировать :)
            pass
        except:
            logging.error("Exception occurred", exc_info=True)
        # # # # # # # # # # # # #
        # # # # # # # # # # # # #
        # # # # # # # # # # # # #

        self.imholder.start()

    def destruct(self):
        self.alive = False
        # block_system()
        self.imholder.alive = False
        with self.lock:
            if self.restarted is False:
                # block_system()
                if AUTORUN is True: Schedule().add_schedule()
                logging.error('ПОПЫТКА ОСТАНОВКИ ПРОЦЕССА')
                send_msg("Убийство процесса")
                stop_service()
                # shutdown_system()
        os.kill(os.getpid(), signal.SIGINT)

    def check_pid(self, interval=0.1):
        while self.alive:
            time.sleep(interval)
            exists = psutil.pid_exists(self.pid)
            if exists is False:
                self.destruct()

    def start_checking(self):
        if self.alive is False:
            self.alive = True
            self.check = Thread(target=self.check_pid)
            self.check.start()

    def stop_checking(self):
        if self.alive is True:
            self.alive = False

    def create_shield(self, pid):
        process = Popen([PATH_, str(pid)])
        self.pid = process.pid
        print(pid, self.pid)
        create_and_start_service(PATH_, pid, self.pid)

    def __exit__(self, type, value, traceback):
        self.alive = False
        self.imholder.alive = False


class Triada:
    def __init__(self, pid_control, pid_shield):
        self.pid_control, self.pid_shield = pid_control, pid_shield
        while True:
            self.start()

    def start(self):

        # самоуничтожение и перезапуск ПО
        # print(self.pid_control, self.pid_shield)

        if psutil.pid_exists(int(self.pid_control)) is not True\
                and psutil.pid_exists(int(self.pid_shield)) is not True:
            # block_system()
            if AUTORUN is True: Schedule().add_schedule()
            logging.error('ПОПЫТКА ОСТАНОВКИ ПРОЦЕССА')
            send_msg('ДВОЙНОЕ УБИЙСТВО ПРОЦЕССОВ!', 'ТРЕВОГА!')
            stop_service()
            # shutdown_system()
            os.kill(os.getpid(), signal.SIGINT)
        # проверка, запущена ли служба. Если нет, удаление службы, блокировка
        # пересоздание планировщика, убийство процесса и перезагрузка системы


# <============================> #
# <========== LAUNCH ==========> #
# <============================> #


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            control = Control()
        elif len(sys.argv) == 2:
            pid = int(sys.argv[1])
            shield = Shield(pid)
        elif len(sys.argv) == 3:
            pid_control = int(sys.argv[1])
            pid_shield = int(sys.argv[2])
            triada = Triada(pid_control, pid_shield)
    except:
        logging.error("Exception occurred", exc_info=True)
