import ctypes
from time import sleep

import poser

poser.Scene().Render()
sleep(30)
ctypes.windll.powrprof.SetSuspendState(True, False, False)
