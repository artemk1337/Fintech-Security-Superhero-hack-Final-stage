import winreg as reg
import os

# POWER_SHELL: Get-CimInstance Win32_StartupCommand | Select-Object * | Format-List
# regedit: Компьютер\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

# https://29a.ch/2009/3/17/autostart-autorun-with-python
# https://github.com/ThomasThelen/Disable-Task-Manager/blob/master/DisableTaskManager.py
# https://www.programcreek.com/python/example/32440/subprocess.SW_HIDE


"""
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunOnce
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServices
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\RunServicesOnce
HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\Windows 
"""


def AddToRegistry():
    # in python __file__ is the instant of
    # file path where it was executed
    # so if it was executed from desktop,
    # then __file__ will be
    # c:\users\current_user\desktop
    pth = os.path.dirname(os.path.realpath(__file__))

    # name of the python file with extension
    s_name = 'test1.py'

    # joins the file name to end of path address
    address = pth + '\\' + s_name
    # print(address)

    # key we want to change is HKEY_CURRENT_USER
    # key value is Software\Microsoft\Windows\CurrentVersion\Run
    key = reg.HKEY_CURRENT_USER
    key_value = 'Software\Microsoft\Windows\CurrentVersion\Run'

    # print(reg.QueryValueEx(key, key_value))
    # quit()

    # open the key to make changes to
    open = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)

    # modifiy the opened key
    reg.SetValueEx(open, "system64", 0, reg.REG_SZ, address)

    # now close the opened key
    reg.CloseKey(open)


# Driver Code
if __name__ == "__main__":
    AddToRegistry()
