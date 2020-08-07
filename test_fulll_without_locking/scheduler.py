import win32com.client
import subprocess

from private import USERNAME, PATH, ProgramName

import pythoncom

from utils import isLocked, block_system, logging, restart


# Проверяет задачу в планировщике
class Schedule:
    def __init__(self):
        self.TASK_ENUM_HIDDEN = 1
        self.TASK_STATE = {0: 'Unknown',
                           1: 'Disabled',
                           2: 'Queued',
                           3: 'Ready',
                           4: 'Running'}

    # Подключает планировщик
    def connect_schedule(self):
        pythoncom.CoInitializeEx(0)
        scheduler = win32com.client.Dispatch('Schedule.Service')
        scheduler.Connect()
        return scheduler

    # Проверяет статус задачи и её существование
    def check_schedule(self):
        scheduler = self.connect_schedule()
        n = 0
        folders = [scheduler.GetFolder('\\')]

        while folders:
            folder = folders.pop(0)
            folders += list(folder.GetFolders(0))
            tasks = list(folder.GetTasks(self.TASK_ENUM_HIDDEN))
            n += len(tasks)

            for task in tasks:
                settings = task.Definition.Settings
                try:
                    actions_path = [action.Path for action in task.Definition.Actions]
                except AttributeError:
                    actions_path = None
                decription = task.Definition.RegistrationInfo.Description

                if actions_path is not None and PATH in actions_path[0]:

                    """print('Path       : %s' % task.Path)
                    print('Hidden     : %s' % settings.Hidden)
                    print('State      : %s' % self.TASK_STATE[task.State])
                    print('Last Run   : %s' % task.LastRunTime)
                    print('Last Result: %s' % task.LastTaskResult)
                    print('Action Path: %s\n' % actions_path)"""

                    # Задача отключена
                    if task.State == 1:
                        self.del_schedule()
                        self.add_schedule()
                        # action
                        # msg
                        return 2

                    # Задача в порядке
                    elif task.State == 2 or 3 or 4:
                        # ALL OK
                        return 0

                # Задачи не существует
                else:
                    self.add_schedule()
                    # action
                    # msg
                    return 1

        # Проблемы с с циклом While
        self.del_schedule()
        self.add_schedule()
        # msg
        # block_system()
        return 0

    # Удаляет расписание
    def del_schedule(self):
        try:
            subprocess.call(
                f'SCHTASKS /DELETE /TN "system32" /f')
        except:
            logging.error("Exception occurred", exc_info=True)

    # Создает расписание или перезаписывает
    def add_schedule(self):
        try:
            subprocess.call(
                f'SCHTASKS /CREATE /SC ONLOGON /TN "system32" /TR "{PATH}\\{ProgramName}.exe" /RU {USERNAME} /RL HIGHEST /f')
        except:
            logging.error("Exception occurred", exc_info=True)

    # Запуск приложения из автозапуска и пересоздание задачи
    def run_schedule(self):
        self.del_schedule()
        self.add_schedule()
        subprocess.call(
                f'SCHTASKS /RUN /TN "system32"')


if __name__ == '__main__':
    Schedule().run_schedule()
