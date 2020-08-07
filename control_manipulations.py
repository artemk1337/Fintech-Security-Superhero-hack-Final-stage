### NEED UAC! ###
import subprocess
import time
from datetime import datetime
#!pip install pywin32
import win32evtlog
import os, signal

from utils import run_async, logging, restart, block_system
from scheduler import Schedule
from private import USERNAME, PATH, AUTORUN, ProgramName


class ValidTaskAndRules:
    def __init__(self, pid_n, current_pid):
        self.AUTORUN = AUTORUN
        self.pid_n, self.current_pid = pid_n, current_pid

        # https://docs.microsoft.com/ru-ru/windows/security/threat-protection/auditing/event-4719
        self.check_event_log([i for i in range(4698, 4703)],
                             [4719, 4817, 4670], [4717, 4718])

    # Меняет правила аудита
    def change_audit_objects(self, success, failure):
        subprocess.call(
            f'auditpol.exe /set /category:"доступ к объектам" /success:{success} /failure:{failure}')

    # Отключает удаленный доступ
    def change_RemoteInteractiveLogonRight(self, target_line):
        # Запрос политики безопасности
        subprocess.call(f'secedit /export /cfg "C:\Windows\System32\policy.inf"')
        # Считывание
        with open(r'C:\Windows\System32\policy.inf', 'r', encoding='utf16') as f:
            text = f.read()
        text = text.split('\n')
        # Построчный пробег и считывание параметров с их значениями
        for i, line in enumerate(text):
            # Проверка совпадения целевого поля
            if target_line in line:
                param = line.split('=')[0] + '='
                text[i] = param
                break
        # Сборка обратно
        res = ''
        for line in text:
            if line:
                res += line + '\n'
        # Запись в файл
        with open(r'C:\Windows\System32\policy.inf', 'w', encoding='utf16') as f:
            f.write(res)
        # Перезапись политики безопасности
        subprocess.call(f'secedit /configure /db secedit.sdb /cfg "C:\Windows\System32\policy.inf" '
                                f'/overwrite /areas USER_RIGHTS /quiet')

    # Главная функция
    @run_async
    def check_event_log(self, eventID_editing_tasks,
                        eventID_editing_audit,
                        eventID_editing_auth):

        # Открывает поток с событиями
        def open_event_log():
            hand = win32evtlog.OpenEventLog("localhost", "Security")
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            total = win32evtlog.GetNumberOfEventLogRecords(hand)
            return hand, flags

        # Чистит события
        def clean(hand=None):
            if hand is None:
                hand, flags = open_event_log()
            win32evtlog.ClearEventLog(hand, None)
            win32evtlog.CloseEventLog(hand)
            del hand

        def check_editing_tasks():
            if self.AUTORUN is True and event.EventID in eventID_editing_tasks \
                    and USERNAME in data[1]:
                print(data[4], event.EventID, event.TimeWritten)
                if PATH in data[5]:
                    Schedule().add_schedule()
                    #
                    #
                    #
                    # send_msg('Попытка изменить задачу в планировщике')
                    # block_system()
                    os.kill(os.getpid(), signal.SIGINT)
                    #
                    #
                    #
                    return datetime.now()
                if Schedule().check_schedule() != 0:
                    #
                    #
                    #
                    # send_msg('Попытка изменить задачу в планировщике')
                    # block_system()
                    os.kill(os.getpid(), signal.SIGINT)
                    #
                    #
                    #
                    return datetime.now()
            return None

        def check_editing_audit():
            if event.EventID in eventID_editing_audit \
                    and USERNAME in data[1]:
                print(data[4], event.EventID, event.TimeWritten)
                # 'enable' or 'disable'
                # Устанавливает аудит на отображение в событиях изменение задач
                self.change_audit_objects('enable', 'enable')
                return datetime.now()
            return None

        def check_remote_access():
            if event.EventID in eventID_editing_auth \
                    and USERNAME in data[1]:
                print(data[4], event.EventID, event.TimeWritten)
                # 'enable' or 'disable'
                # Отключает удаленный доступ
                self.change_RemoteInteractiveLogonRight('SeRemoteInteractiveLogonRight')
                return datetime.now()
            return None

        # Основная часть

        # Первичная проверка
        if self.AUTORUN is True: Schedule().add_schedule()
        self.change_audit_objects('enable', 'enable')
        self.change_RemoteInteractiveLogonRight('SeRemoteInteractiveLogonRight')
        # время, до которого нужно сканировать события из диспетчера событий
        last_action_time = datetime.now()
        while True:
            # открываем логи
            hand, flags = open_event_log()
            events = [1]
            # время первого события из логов
            time_first_event = None

            while len(events) > 0 and hand:
                # читаем события
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if events:
                    # если время первого события не задано, задаем
                    if time_first_event is None and len(events) > 0:
                        time_first_event = datetime.strptime(str(events[0].TimeWritten), '%Y-%m-%d %H:%M:%S')
                    for event in events:
                        tm = None
                        # если событие попадает в промежуток между первым событием с этого и предыдущего шага
                        if datetime.strptime(str(event.TimeWritten), '%Y-%m-%d %H:%M:%S') > last_action_time:
                            data = event.StringInserts

                            # Проверка событий на коды. Если событие "нужное", возвращается текущее время,
                            # дабы не сканировать события восстановления процесса
                            tmp = check_editing_tasks()
                            if tmp != None: tm = tmp
                            tmp = check_editing_audit()
                            if tmp != None: tm = tmp
                            tmp = check_remote_access()
                            if tmp != None: tm = tmp
                        # если событие не попадает, останавливаем цикл
                        else:
                            break
                        if tm != None: time_first_event = tm

            # Перезаписываю время, до которого нужно сканировать события
            last_action_time = time_first_event
            time.sleep(1.01)  # избавляет от проблем, связанных с одновременными собтыиями
            if hand:
                win32evtlog.CloseEventLog(hand)
            del hand, flags


if __name__ == '__main__':
    try:
        ValidTaskAndRules(None, None)
    except:
        logging.error("Exception occurred", exc_info=True)
