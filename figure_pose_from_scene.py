import poser
from typing import Dict, Set, Tuple


def pose(pz3: str) -> None:
    """
    Poses the current figure using a PZ3 text file
    and asks the user to pose according to which figure and keyframe
    """

    # detect all figures
    figures: Dict[str, int] = {}
    cur = 0
    while True:
        cur = pz3.find('figure \n	{\n	name    ', cur)
        if cur == -1: break
        cur += 20
        figure_name = pz3[cur:pz3.find('\n', cur)]
        cur = pz3.find('Figure ', cur) + 7
        figure_id = int(pz3[cur:pz3.find('\n', cur)])
        figures[figure_name] = figure_id

    if len(figures) == 0:
        poser.DialogSimple.MessageBox('This scene has no poses.')
        return

    # let the user choose a figure
    if len(figures) > 1:
        chosen_figure = poser.DialogSimple.AskMenu(
            'Pose from Scene', 'Choose a figure:', tuple(figures.keys()))
        if chosen_figure is None or len(chosen_figure) == 0: return
        figure_id = figures[chosen_figure]
    else:
        figure_id = list(figures.values())[0]

    # analyse the source pose and gather keyframes
    scene = poser.Scene()
    figure = scene.CurrentFigure()
    pose: Dict[str, Dict[str, Dict[int, float]]] = {}
    keyframes: Set[str] = set()
    for actor in figure.Actors():
        if not actor.IsBodyPart(): continue
        actor_name = actor.InternalName().rsplit(':', 1)[0]
        if actor_name in ['bodyMorphs']: continue
        pose[actor_name] = {}

        # find the right actor
        try:
            min_actor_cur, max_actor_cur = find_actor(pz3, actor_name, figure_id)
        except ValueError:
            poser.DialogSimple.MessageBox('Incompatible figure!')
            return

        # queue the right parameters for synchronisation
        parms = ['rotateX xrot', 'rotateY yrot', 'rotateZ zrot']
        if actor_name == 'hip':
            parms.extend(['targetGeom PBMGluteFlexL', 'targetGeom PBMGluteFlexR'])
        if actor_name == 'chest':
            parms.append('targetGeom PBMInhale')
            for morph in breast_movements:
                parms.append('targetGeom ' + morph)
            for morph in jaw_dropper:
                parms.append('targetGeom ' + morph)
        if actor_name == 'head':
            for morph in expressions:
                parms.append('targetGeom ' + morph)
            for morph in eye_controls:
                parms.append('targetGeom ' + morph)
        if actor_name.startswith('tongue'):
            parms.append('scaleZ zScale')
        if actor_name in ['rShldr', 'lShldr']:
            parms.append('targetGeom PBMBicepFlex')
        if actor_name in ['rHand', 'lHand']:
            for morph in finger_controls:
                parms.append('targetGeom ' + morph)  # targetGeom-ness affirmed!
        if actor_name in ['rShin', 'lShin']:
            parms.append('targetGeom PBMCalfFlex')
        if actor_name in ['rFoot', 'lFoot']:
            parms.append('targetGeom PBMFootForShoe')
        if actor_name in ['rToe', 'lToe']:
            for morph in toe_controls:
                parms.append('targetGeom ' + morph)

        for parm_title in parms:
            parm_name = parm_title.split(' ')[1]
            parm = actor.Parameter(parm_name)
            if parm is None: continue
            pose[actor_name][parm_name] = {}
            try:
                min_parm_cur, max_parm_cur = find_parm(pz3, parm_title, min_actor_cur, max_actor_cur)
            except ValueError:
                pose[actor_name][parm_name][0] = parm.InitValue()
                continue

            # extract keyframes
            cur = min_parm_cur
            while True:
                try:
                    cur = pz3.index('				k  ', cur, max_parm_cur) + 4
                    kv = pz3[cur:pz3.index('\n', cur)].split('  ')
                    pose[actor_name][parm_name][int(kv[1])] = float(kv[2])
                    keyframes.add(kv[1])
                except ValueError:
                    break

    # let the use choose a keyframe if multiple keyframes are detected
    chosen_keyframe = None
    if len(keyframes) > 1:
        chosen_keyframe = poser.DialogSimple.AskMenu(
            'Pose from Scene', 'Choose a keyframe:', tuple(keyframes))
        if chosen_keyframe is None or len(chosen_keyframe) == 0: return

    # finally apply the pose on the current figure
    for body_part in pose:
        actor = figure.Actor(body_part)
        for parm_name in pose[body_part]:
            k = int(list(pose[body_part][parm_name])[0]) if chosen_keyframe is None else int(chosen_keyframe)

            if k not in pose[body_part][parm_name]:
                k_plus, k_minus = k, k
                while k_minus not in pose[body_part][parm_name]:
                    k_minus -= 1
                    if k_minus == -1: break
                else:
                    k = k_minus
                while k_plus not in pose[body_part][parm_name]:
                    k_plus += 1
                    if k_plus == 1800: break
                else:
                    k = k_plus

            try:
                actor.Parameter(parm_name).SetValue(pose[body_part][parm_name][k])
            except Exception as e:
                print(body_part, parm_name, k)
                raise e
    scene.Draw()


def find_actor(pz3: str, actor_name_: str, figure_id_: int) \
        -> Tuple[int, int]:
    min_ = pz3.rindex(f'actor {actor_name_}:{figure_id_}\n	')
    max_ = pz3.index('\n	}\n', min_)
    return min_, max_


def find_parm(pz3: str, parm_: str, min_actor_cur_: int, max_actor_cur_: int) \
        -> Tuple[int, int]:
    min_ = pz3.index(parm_ + '\n			{', min_actor_cur_, max_actor_cur_)
    max_ = pz3.index('\n			}\n', min_)
    return min_, max_


# TODO body controls

# noinspection SpellCheckingInspection
expressions = [
    'PHMBrowUp-Down', 'PHMBrowUp-DownR', 'PHMBrowUp-DownL',
    'PHMBrowOuterUp-Down', 'PHMBrowOuterUp-DownR', 'PHMBrowOuterUp-DownL',
    'PHMBrowInnerUp-Down', 'PHMBrowInnerUp-DownR', 'PHMBrowInnerUp-DownL',
    'PHMBrowSqueeze',
    'PHMEyesSquint', 'PHMEyeSquintR', 'PHMEyeSquintL',
    'PHMEyesOpen-Close',
    'PHMEyeOpen-CloseR', 'PHMEyeLidTopUp-DownR', 'PHMEyeLidBottomUp-DownR',
    'PHMEyeOpen-CloseL', 'PHMEyeLidTopUp-DownL', 'PHMEyeLidBottomUp-DownL',
    'PHMNoseWrinkle', 'PHMNostrilsFlare',
    'PHMCheeksEyeFlex', 'PHMCheekEyeFlexR', 'PHMCheekEyeFlexL',
    'PHMCheeksFlex', 'PHMCheekFlexR', 'PHMCheekFlexL',
    'PHMCheeksCrease', 'PHMCheekCreaseR', 'PHMCheekCreaseL',
    'PHMCheeksBalloon', 'PHMCheeksBalloonPucker',
    'PHMMouthSmileSimple', 'PHMMouthSmileOpen',
    'PHMMouthSmile-Frown', 'PHMMouthSmile-FrownR', 'PHMMouthSmile-FrownL',
    'PHMMouthSneer-Pout', 'PHMMouthSneer-PoutR', 'PHMMouthSneer-PoutL',
    'PHMMouthSide-Side',
    'PHMMouthNarrow', 'PHMMouthNarrowR', 'PHMMouthNarrowL',
    'PHMMouthCornerUp-Down',
    'PHMMouthOpen', 'PHMMouthOpenWide',
    'PHMJawIn-Out', 'PHMJawSide-Side',
    'PHMLipsPart', 'PHMLipsPartCenter', 'PHMLipsPucker', 'PHMLipsPuckerWide',
    'PHMLipTopUp-Down', 'PHMLipTopUp-DownR', 'PHMLipTopUp-DownL',
    'PHMLipBottomUp-Down', 'PHMLipBottomUp-DownR', 'PHMLipBottomUp-DownL',
    'PHMLipBottomIn-Out', 'PHMLipBottomIn-OutR', 'PHMLipBottomIn-OutL',

    'VSM_IY', 'VSM_IH', 'VSM_EH', 'VSM_AA', 'VSM_OW', 'VSM_UW', 'VSM_ER', 'VSM_S',
    'VSM_SH', 'VSM_F', 'VSM_TH', 'VSM_M', 'VSM_T', 'VSM_L', 'VSM_W', 'VSM_K'
]

# noinspection SpellCheckingInspection
eye_controls = ['CTRLEyesUp-Down', 'CTRLEyesSide-Side']

# noinspection SpellCheckingInspection
breast_movements = [
    'PBMBreastDownL', 'PBMBreastDownR', 'PBMBreastUpL', 'PBMBreastUpR',
    'PBMBreastInL', 'PBMBreastInR', 'PBMBreastOutL', 'PBMBreastOutR'
]

# noinspection SpellCheckingInspection
jaw_dropper = [
    'BreastSoft_SupermorphR', 'BreastSoft_SupermorphL',
    'BreastSoft_ArmSqueezeR', 'BreastSoft_ArmSqueezeL',
    'BreastSoft_LayingDownR', 'BreastSoft_LayingDownL',
    'BreastSoft_OnPlaneR', 'BreastSoft_OnPlaneL',
    'BreastSoft_SidetoSideBothR', 'BreastSoft_SidetoSideBothL',
    'BreastSoft_BreastOutR', 'BreastSoft_BreastOutL',
    'BreastSoft_RaiseR', 'BreastSoft_RaiseL',
    'BreastSoft_Cleavage', 'BreastSoft_CleavagePlusR', 'BreastSoft_CleavagePlusL',
    'Nipple_Side-SideR', 'Nipple_Side-SideL',
    'Nipple_Up-DownR', 'Nipple_Up-DownL'
]

# noinspection SpellCheckingInspection
finger_controls = [
    'CTRLHandGrasp', 'CTRLHandSpread',
    'CTRLThumbGrasp', 'CTRLIndexGrasp', 'CTRLMiddleGrasp', 'CTRLRingGrasp', 'CTRLPinkyGrasp'
]

# noinspection SpellCheckingInspection
toe_controls = [
    'PBMToeBigCurl', 'PBMToeBigUp-Down', 'PBMToeBigSide-Side',
    'PBMToesSmallUp-Down', 'PBMToesSmallIn', 'PBMToePointed'
]

if __name__ == '__main__':
    file_chooser = poser.DialogFileChooser(
        poser.kDialogFileChooserOpen, None, f'Select a Poser scene file')
    continuum = file_chooser.Show() == 1

    if continuum:
        pose(open(file_chooser.Path(), 'r').read())
