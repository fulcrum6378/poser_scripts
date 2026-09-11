import poser
from typing import Dict, List

CHARACTERS: Dict[str, str] = {
    'C': 'CHRISTIE',
    'E': 'ESPINELA',
    'L': 'LUNA',
    'M': 'MAHDI',
    'T': 'TRIJNTJE',
    'Z': 'ZOEY',
}

# noinspection SpellCheckingInspection
actors: List[str] = [
    'BODY', 'hip', 'abdomen', 'chest', 'neck',
    'head', 'rEye', 'lEye', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'tongue05', 'tongueTip',
    'rCollar', 'rShldr', 'rForeArm', 'rHand',
    'rThumb1', 'rThumb2', 'rThumb3',
    'rIndex1', 'rIndex2', 'rIndex3',
    'rMid1', 'rMid2', 'rMid3',
    'rRing1', 'rRing2', 'rRing3',
    'rPinky1', 'rPinky2', 'rPinky3',
    'lCollar', 'lShldr', 'lForeArm', 'lHand',
    'lThumb1', 'lThumb2', 'lThumb3',
    'lIndex1', 'lIndex2', 'lIndex3',
    'lMid1', 'lMid2', 'lMid3',
    'lRing1', 'lRing2', 'lRing3',
    'lPinky1', 'lPinky2', 'lPinky3',
    'rThigh', 'rShin', 'rFoot', 'rToe',
    'lThigh', 'lShin', 'lFoot', 'lToe'
]
# noinspection SpellCheckingInspection
expressions: List[str] = [
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
jaw_dropper: List[str] = [
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
rotations: Dict[str, str] = {'yrot': 'rotateY', 'xrot': 'rotateX', 'zrot': 'rotateZ'}


def extract_pose(figure: poser.FigureType) -> str:
    global actors, jaw_dropper, rotations
    pz2 = '{\n\nversion\n	{\n	number 14\n	}\n'
    for actor_name in actors:
        pz2 += '\nactor ' + actor_name + '\n	{\n	channels\n		{\n'
        actor = figure.Actor(actor_name)

        if actor_name == 'chest':
            if figure.Name() == 'LUNA':
                for parm_name in jaw_dropper:
                    pz2 += extract_parameter(actor, 'targetGeom', parm_name, True)

        if actor_name == 'head':
            for parm_name in expressions:
                pz2 += extract_parameter(actor, 'targetGeom', parm_name, True)

        if actor_name.startswith('tongue'):
            pz2 += extract_parameter(actor, 'scaleZ', 'zScale', False)

        for parm in actor.Parameters():
            parm_name = parm.InternalName()
            if not parm_name.endswith('rot') or len(parm_name) != 4: continue
            pz2 += extract_parameter(actor, rotations[parm_name], parm_name, False)

        pz2 += '		}\n	}\n'
    pz2 += '}\n'
    return pz2


def extract_parameter(actor: poser.ActorType, parm_type: str, parm_name: str,
                      use_unaffected_value: bool) -> str:
    parm = actor.Parameter(parm_name)
    if parm is None:
        val = '0'
    else:
        if not use_unaffected_value:
            val = parm.Value()
        else:
            val = parm.UnaffectedValue()
        if val % 1 == 0:
            val = str(int(val))
        else:
            for decimals in range(6):
                rounded = round(val, decimals)
                if abs(val - rounded) < 0.000001:
                    val = rounded
                    break
            val = str(val).rstrip('0').rstrip('.')
    return '		' + parm_type + ' ' + parm_name + \
        '\n			{\n			keys\n				{\n				k  0  ' + val + \
        '\n				}\n			}\n'
