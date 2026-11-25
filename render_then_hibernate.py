import ctypes
import os
import poser
from time import sleep, time

from commons import DESKTOP

begin = time()
poser.Scene().Render()
finish = time()

if (finish - begin) > (60 * 10) and 'KEEPALIVE' not in os.listdir(DESKTOP):
    sleep(10)
    ctypes.windll.powrprof.SetSuspendState(True, False, False)
