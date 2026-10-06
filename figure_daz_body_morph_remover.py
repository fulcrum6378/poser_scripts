import poser
from typing import List

text_entry = poser.DialogTextEntry(0, 'What FBM/PBM morphs to exclude?\n(use `,` for separation)')
if text_entry.Show() == 1:
    selection: List[str] = text_entry.Text().strip().split(',')

    del_morph, del_parm = 0, 0
    for actor in poser.Scene().CurrentFigure().Actors():
        for parm in actor.Parameters():
            parm_vis_name = parm.Name()
            parm_int_name = parm.InternalName()
            if (parm_int_name.startswith('FBM') or parm_int_name.startswith('PBM')) and \
                    parm_vis_name not in selection and parm_int_name not in selection and \
                    parm.Value() == 0:
                try:
                    if parm.IsMorphTarget():
                        actor.DeleteTarget(parm_vis_name)
                        del_morph += 1
                    else:
                        actor.RemoveValueParameter(parm_vis_name)
                        del_parm += 1
                except:
                    pass

    poser.DialogSimple.MessageBox(f'{del_morph} morphs and {del_parm} parameters were deleted.')
