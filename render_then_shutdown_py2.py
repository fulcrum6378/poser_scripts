import os
import poser
from time import sleep, time

begin = time()
poser.Scene().Render()
finish = time()

if (finish - begin) > (60 * 5):
    sleep(15)
    os.system("shutdown /s /t 0")
    poser.Quit(1)
