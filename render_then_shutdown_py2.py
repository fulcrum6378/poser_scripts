import os
import poser
from time import sleep

poser.Scene().Render()
sleep(15)
os.system("shutdown /s /t 0")
