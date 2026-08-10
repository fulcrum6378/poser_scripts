import os

if 'INNOVATION' not in os.listdir(os.environ['USERPROFILE'] + '\\Desktop'):
    for actor in poser.Scene().CurrentFigure().Actors():
        for param in actor.Parameters():
            if param.Name().startswith('EMPTY-') or param.Name() == '-':
                if param.IsMorphTarget():
                    actor.DeleteTarget(param.Name())
                else:
                    actor.RemoveValueParameter(param.Name())
