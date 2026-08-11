import os

import poser

import pose_extractor as psx


def get_pose_dir(album_id: str, album_name: str) -> str:
    for library in poser.Libraries():
        if 'OneDrive' in library:
            runtime_dir = library
            break
    return os.path.join(runtime_dir, 'Runtime', 'Libraries', 'Pose', f'{album_id} {album_name}')


def extract_all(scene: poser.SceneType, pose_dir: str, album_id: str, render_id: str) -> int:
    if not os.path.isdir(pose_dir):
        os.mkdir(pose_dir)
    i = 0
    for key, figure_name in psx.CHARACTERS.items():
        try:
            figure = scene.Figure(figure_name)
        except poser.error:
            continue

        pz2_path = os.path.join(pose_dir, f'{album_id}-{render_id} ({key}).pz2')
        if os.path.isfile(pz2_path):
            raise FileExistsError('Please be careful!')
        scene.SelectFigure(figure)
        open(pz2_path, 'w', encoding='cp1252', newline='\n').write(psx.extract_pose(figure))
        i += 1
    return i


if __name__ == '__main__':

    # determine the initial values
    scene = poser.Scene()
    album = os.path.dirname(scene.DocumentPath())
    if os.path.basename(album)[2:4] != '. ':
        raise Exception('This document is not a Fantasy scene.')
    album_id, album_name = os.path.basename(album).split('. ')

    # determine the destination
    pose_dir = get_pose_dir(album_id, album_name)
    if not os.path.isdir(pose_dir):
        render_id = '001'
    else:
        render_id = 1
        for pose in os.listdir(pose_dir):
            if not pose.endswith('.pz2'): continue
            if render_id == int(pose[3:6]):
                render_id += 1
        render_id = f'{render_id:03d}'

    num_poses = extract_all(scene, pose_dir, album_id, render_id)
    if num_poses > 0:
        poser.DialogSimple.MessageBox(f'{num_poses} poses were extracted.')
    else:
        poser.DialogSimple.MessageBox('No poses were extracted.')
