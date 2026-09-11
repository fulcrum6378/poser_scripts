import ctypes
import poser
from time import sleep

poser.Scene().Render()
sleep(30)
ctypes.windll.powrprof.SetSuspendState(True, False, False)
