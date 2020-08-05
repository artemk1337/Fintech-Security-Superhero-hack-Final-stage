# !pip install "setproctitle-1.1.10-cp36-cp36m-win_amd64.whl"

from multiprocessing import Process
import multiprocessing
import time


def count_down(name, delay):
    print('Process %s starting...' % name)

    counter = 5

    while counter > 0:
        time.sleep(delay)
        print('Process %s counting down: %f...' % (name, counter))
        counter -= 0.1

    print('Process %s exiting...' % name)


if __name__ == '__main__':
    # ВАЖНО для Windows!!!
    multiprocessing.freeze_support()

    process1 = Process(target=count_down, args=('A', 0.5), name='TEST1')
    process2 = Process(target=count_down, args=('B', 0.5), name='TEST2')

    process1.start()
    process2.start()

    print('Done.')

