import ctypes
import poser
from time import sleep, time

begin = time()
poser.Scene().Render()
finish = time()

if (finish - begin) > (60 * 5):
    sleep(10)
    ctypes.windll.powrprof.SetSuspendState(True, False, False)
