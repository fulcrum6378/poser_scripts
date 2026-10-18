import os
import poser

from _config import DESKTOP

if 'INNOVATION' not in os.listdir(DESKTOP):
    for actor in poser.Scene().CurrentFigure().Actors():
        for param in actor.Parameters():
            if param.Name().startswith('EMPTY-') or param.Name() == '-':
                if param.IsMorphTarget():
                    actor.DeleteTarget(param.Name())
                else:
                    actor.RemoveValueParameter(param.Name())
