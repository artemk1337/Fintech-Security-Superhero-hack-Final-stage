from subprocess import call, PIPE, check_output
from private import SERVICE_NAME


# nssm import
# sc queryex eventlog Test
# taskkill /pid  /f



def check_status_service():
    try:
        line = f'nssm status {SERVICE_NAME}'
        process = check_output(line)
        process = process.decode('utf-16').encode('utf-8')
        if process == b'SERVICE_STOPPED\r\n':
            line = f'nssm start {SERVICE_NAME}'
            check_output(line)
            return 1
        elif process == b'SERVICE_RUNNING\r\n':
            return 0
    except:
        return -1


def stop_service():
    try:
        line = f'nssm stop {SERVICE_NAME}'
        call(line)
    except:
        pass
    try:
        line = f'nssm remove {SERVICE_NAME} confirm'
        call(line)
    except:
        pass


def create_and_start_service(PATH_, pid1, pid2):
    stop_service()
    try:
        line = f'nssm install {SERVICE_NAME} "{PATH_}" {str(pid1)} {str(pid2)}'
        call(line)
    except:
        pass
    try:
        line = f'nssm start {SERVICE_NAME}'
        print(line)
        call(line)
    except:
        pass

