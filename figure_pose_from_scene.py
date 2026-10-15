import poser
from typing import Dict, Set, Tuple

from character_pose_extractor import expressions, jaw_dropper


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
    chosen_figure = poser.DialogSimple.AskMenu('Pose from Scene', 'Choose a figure:', tuple(figures.keys()))
    if chosen_figure is None or len(chosen_figure) == 0: return
    figure_id = figures[chosen_figure]

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

        # mark the right parameters for synchronisation
        parms = ['rotateX xrot', 'rotateY yrot', 'rotateZ zrot']
        if actor_name == 'chest':
            for morph in jaw_dropper:
                parms.append('targetGeom ' + morph)
        if actor_name == 'head':
            for expression in expressions:
                parms.append('targetGeom ' + expression)
        if actor_name.startswith('tongue'):
            parms.append('scaleZ zScale')

        for parm in parms:
            parm_name = parm.split(' ')[1]
            if actor.Parameter(parm_name) is None: continue
            try:
                min_parm_cur, max_parm_cur = find_parm(pz3, parm, min_actor_cur, max_actor_cur)
            except ValueError:
                continue
            pose[actor_name][parm_name] = {}

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


def find_actor(pz3: str, actor_name_: str, figure_id_: int) -> Tuple[int, int]:
    min_ = pz3.rindex(f'actor {actor_name_}:{figure_id_}\n	')
    max_ = pz3.index('\n	}\n', min_)
    return min_, max_


def find_parm(pz3: str, parm_: str, min_actor_cur_: int, max_actor_cur_: int) -> Tuple[int, int]:
    min_ = pz3.index(parm_ + '\n			{', min_actor_cur_, max_actor_cur_)
    max_ = pz3.index('\n			}\n', min_)
    return min_, max_


if __name__ == '__main__':
    file_chooser = poser.DialogFileChooser(
        poser.kDialogFileChooserOpen, None, f'Select a Poser scene file')
    continuum = file_chooser.Show() == 1

    if continuum:
        pose(open(file_chooser.Path(), 'r').read())
