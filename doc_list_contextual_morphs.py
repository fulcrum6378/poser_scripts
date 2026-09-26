import poser
from typing import List

scene = poser.Scene()
morphed_actors: List[str] = []
for actor in scene.Actors():
    if actor.IsProp() or actor.Name() == 'Body':
        for parm in actor.Parameters():
            if parm.IsMorphTarget() and 'Contextual' in parm.Name():
                name = actor.Name()
                if actor.ItsFigure() is not None:
                    name = actor.ItsFigure().Name() + '\'s ' + name
                name += ': ' + parm.Name()
                morphed_actors.append(name)

if len(morphed_actors) > 0:
    poser.DialogSimple.MessageBox('\n'.join(morphed_actors))
else:
    poser.DialogSimple.MessageBox('This scene has no contextual morphs.')
