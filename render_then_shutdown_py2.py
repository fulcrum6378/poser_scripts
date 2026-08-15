import os
from time import sleep

import poser

poser.Scene().Render()
sleep(15)
os.system("shutdown /s /t 0")
