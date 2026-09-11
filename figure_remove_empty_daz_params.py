import poser

morphs_removed, parms_removed = 0, 0
for actor in poser.Scene().CurrentFigure().Actors():
    removed = ''
    for param in actor.Parameters():
        if param.Name().startswith('EMPTY-') or param.Name() == '-':
            if param.IsMorphTarget():
                actor.DeleteTarget(param.Name())
                morphs_removed += 1
            else:
                actor.RemoveValueParameter(param.Name())
                parms_removed += 1
            removed += ' ' + param.Name()
    if len(removed) > 0:
        print('Parameters removed from', actor.Name(), 'are:' + removed)
print(f'\n\nOverall, {morphs_removed} morphs and {parms_removed} '
       'value parameters were removed from this figure.')
