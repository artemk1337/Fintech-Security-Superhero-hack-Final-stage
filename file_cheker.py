import os
import win32security
import ntsecuritycon as con
import win32net
import win32netcon
import subprocess

from private import PATH, ProgramName
from utils import logging, send_msg, block_system


# нужно будет добавить копирование nssm.exe в папку c:/Windows/System32


class CheckFiles:
    def __init__(self):
        pass

    def check_path(self, path_, error_message):
        if not os.path.isfile(path_):
            logging.error(error_message)
            send_msg(error_message)
            # block_system
            return False
        return True

    def change_permissions(self, path_, action):
        def listusers(server=None):
            level = 0
            filter = win32netcon.FILTER_NORMAL_ACCOUNT
            resume_handle = 0
            user_list = []
            while True:
                result = win32net.NetUserEnum(server, level, filter, resume_handle)
                user_list += [user['name'] for user in result[0]]
                resume_handle = result[2]
                if not resume_handle:
                    break
            user_list.sort()
            return user_list

        for user in listusers():
            # print(user, path_)
            userx, domain, type = win32security.LookupAccountName("", user)

            sd = win32security.GetFileSecurity(path_, win32security.DACL_SECURITY_INFORMATION)
            dacl = sd.GetSecurityDescriptorDacl()   # instead of dacl = win32security.ACL()

            if action == 0:
                try:
                    dacl.DeleteAce(win32security.ACL_REVISION)
                except:
                    pass
            else:
                dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_GENERIC_EXECUTE | con.FILE_GENERIC_READ, userx)

            sd.SetSecurityDescriptorDacl(1, dacl, 0)   # may not be necessary
            win32security.SetFileSecurity(path_, win32security.DACL_SECURITY_INFORMATION, sd)

    def exist_files_and_permission(self):
        if self.check_path(PATH + '\\' + ProgramName + '.exe', 'Удаление файла программы!') is False \
                or self.check_path(r'C:\WINDOWS\System32\nssm.exe', 'Удаление файла nssm!') is False:
            pass
        else:
            subprocess.call(f'icacls "{PATH}\\{ProgramName}.exe" /inheritance:e', shell=True)
            for i in range(3):
                self.change_permissions(PATH + '\\' + ProgramName + '.exe', 0)
            self.change_permissions(PATH + '\\' + ProgramName + '.exe', 1)
            # self.change_permissions(r'C:\WINDOWS\System32\nssm.exe', 0)
            # self.change_permissions(r'C:\WINDOWS\System32\nssm.exe', 1)
            pass


if __name__ == "__main__":
    CheckFiles().exist_files_and_permission()
