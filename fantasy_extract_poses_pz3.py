import os
from typing import Dict, Optional, Tuple

from pose_extractor import actors, expressions, jaw_dropper

CHARACTERS: Dict[str, str] = {
    'CHRISTIE': 'C',
    'ESPINELA': 'E',
    'LUNA': 'L',
    'MAHDI': 'M',
    'TRIJNTJE': 'T',
    'ZOEY': 'Z',
}
morph_forms: Dict[str, float] = {}


def extract_all(pz3_path: str, pose_dir: str, album_id: str, render_id: str) -> int:
    global pz3, morph_forms, min_actor_cur, max_actor_cur
    if not os.path.isdir(pose_dir):
        os.mkdir(pose_dir)

    pz3 = open(pz3_path, 'r').read()

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

    # extract poses
    i = 0
    for figure_name, figure_id in figures.items():
        if figure_name not in CHARACTERS: continue
        pz2 = '{\n\nversion\n	{\n	number 14\n	}\n'

        for actor_name in actors:
            pz2 += '\nactor ' + actor_name + '\n	{\n	channels\n		{\n'

            min_actor_cur, max_actor_cur = find_actor(actor_name, figure_id)

            if actor_name == 'chest':
                if figure_name == 'LUNA':
                    for parm_name in jaw_dropper:
                        pz2 += extract_parameter('targetGeom ' + parm_name, False)

            if actor_name == 'head':
                for parm_name in expressions:
                    pz2 += extract_parameter('targetGeom ' + parm_name, False)

            if actor_name.startswith('tongue'):
                pz2 += extract_parameter('scaleZ zScale', True)

            rotations = {'rotateX xrot': -1, 'rotateY yrot': -1, 'rotateZ zrot': -1}
            for rot in rotations.keys():
                rotations[rot] = pz3.find(rot, min_actor_cur, max_actor_cur)
            rotations = list(dict(sorted(rotations.items(), key=lambda i: i[1])).keys())
            for rot in rotations:
                pz2 += extract_parameter(rot, True)

            pz2 += '		}\n	}\n'
        pz2 += '}\n'

        pz2_path = os.path.join(pose_dir, f'{album_id}-{render_id} ({CHARACTERS[figure_name]}).pz2')
        if os.path.isfile(pz2_path):
            raise FileExistsError('Please be careful!')
        open(pz2_path, 'w', encoding='cp1252', newline='\n').write(pz2)
        morph_forms.clear()
        i += 1
    return i


def extract_parameter(parm: str, resolve_value_ops: bool) -> str:
    global pz3, min_actor_cur, max_actor_cur
    val = resolve_dependencies(parm, min_actor_cur, max_actor_cur, resolve_value_ops, False)
    return '		' + parm + '\n			{\n			keys\n				{\n				' + \
        'k  0  ' + val + '\n				}\n			}\n'


def resolve_dependencies(parm: str, min_actor_cur_: int, max_actor_cur_: int,
                         resolve_value_ops: bool, is_morph_form: bool):
    global morph_forms
    min_parm_cur, max_parm_cur = find_parm(parm, min_actor_cur_, max_actor_cur_)
    if min_parm_cur == -1:
        if not is_morph_form:
            print(f'{parm} is unavailable. Defaulted to 0.')
            return '0'
        else:
            raise SyntaxError(f'Necessary morph-form {parm} is not available!')

    min_limit: Optional[float] = None
    max_limit: Optional[float] = None
    if resolve_value_ops:
        cur = pz3.find('			min ', min_parm_cur, max_parm_cur) + 7
        min_limit = float(pz3[cur:pz3.find('\n', cur)])
        cur = pz3.find('			max ', min_parm_cur, max_parm_cur) + 7
        max_limit = float(pz3[cur:pz3.find('\n', cur)])

    cur = pz3.rfind('				k  ', min_parm_cur, max_parm_cur)
    val = pz3[cur:pz3.find('\n', cur)].split('  ')[2]

    if resolve_value_ops:
        while True:
            test_dep = pz3.find('			valueOp', cur, max_parm_cur)
            if test_dep == -1: break
            cur = test_dep + 10
            dep_type = pz3[cur:pz3.find('\n', cur)]
            cur = pz3.find('				Figure ', cur, max_parm_cur) + 11
            figure_id_ = int(pz3[cur:pz3.find('\n', cur)])
            cur = pz3.find('				', cur) + 4
            actor_name_ = pz3[cur:pz3.find(':', cur)]
            cur = pz3.find('				', cur) + 4
            dep = pz3[cur:pz3.find('\n', cur)]
            cur = pz3.find('				strength ', cur) + 13
            parm_key = f'{actor_name_}:{figure_id_}_{parm}'
            if parm_key not in morph_forms:
                dep_min_actor, dep_max_actor = find_actor(actor_name_, figure_id_)
                dep_val = resolve_dependencies(dep, dep_min_actor, dep_max_actor,
                                               True, True)
                if is_morph_form:
                    morph_forms[parm_key] = dep_val
            else:
                dep_val = morph_forms[parm_key]
            strength = float(pz3[cur:pz3.find('\n', cur)])
            if dep_type == 'DeltaAdd':
                if isinstance(val, str):
                    val = float(val)
                val += float(dep_val) * strength
            else:
                raise NotImplementedError(dep_type)
        if isinstance(val, float):
            if val > max_limit: val = max_limit
            if val < min_limit: val = min_limit
            if not is_morph_form:
                if val % 1 == 0:
                    val = str(int(val))
                else:
                    for decimals in range(6):
                        rounded = round(val, decimals)
                        if abs(val - rounded) < 1e-8:  # 0.00000001
                            val = rounded
                            break
                    val = str(val).rstrip('0').rstrip('.')
    if not is_morph_form:
        if val == '-0': val = '0'
    else:
        val = float(val)
    return val


def find_parm(parm_: str, min_actor_cur_: int, max_actor_cur_: int) -> Tuple[int, int]:
    global pz3
    min_ = pz3.find(parm_ + '\n			{', min_actor_cur_, max_actor_cur_)
    max_ = pz3.find('\n			}\n', min_)
    return min_, max_


def find_actor(actor_name_: str, figure_id_: int) -> Tuple[int, int]:
    global pz3
    min_ = pz3.rfind(f'actor {actor_name_}:{figure_id_}\n	')
    max_ = pz3.find('\n	}\n', min_)
    return min_, max_


if __name__ == '__main__':

    # determine the initial values
    pz3_path = poser.Scene().DocumentPath()
    album = os.path.dirname(pz3_path)
    if os.path.basename(album)[2:4] != '. ':
        raise Exception('This document is not a Fantasy scene.')
    album_id, album_name = os.path.basename(album).split('. ')

    # determine the destination
    import fantasy_extract_poses as fxp
    pose_dir = fxp.get_pose_dir(album_id, album_name)
    if not os.path.isdir(pose_dir):
        render_id = '001'
    else:
        render_id = 1
        for pose in os.listdir(pose_dir):
            if not pose.endswith('.pz2'): continue
            if render_id == int(pose[3:6]):
                render_id += 1
        render_id = f'{render_id:03d}'

    num_poses = extract_all(pz3_path, pose_dir, album_id, render_id)
    if num_poses > 0:
        poser.DialogSimple.MessageBox(f'{num_poses} poses were extracted.')
    else:
        poser.DialogSimple.MessageBox('No poses were extracted.')
