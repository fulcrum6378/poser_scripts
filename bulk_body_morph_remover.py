from typing import List

import poser

text_entry = poser.DialogTextEntry(0, 'What FBM/PBM morphs to exclude?\n(use `,` for separation)')
if text_entry.Show() == 1:
    selection: List[str] = text_entry.Text().strip().split(',')

    for actor in poser.Scene().CurrentFigure().Actors():
        for parm in actor.Parameters():
            if (parm.InternalName().startswith('FBM') or parm.InternalName().startswith('PBM')) and \
                    parm.InternalName() not in selection:
                if parm.IsMorphTarget():
                    actor.DeleteTarget(parm.Name())
                else:
                    actor.RemoveValueParameter(parm.Name())
