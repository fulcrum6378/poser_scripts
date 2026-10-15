import os
import poser
import subprocess

import figure_pose_from_scene

# determine the Fantasy render ID
text_entry = poser.DialogTextEntry(0, 'Enter the Fantasy render ID:')
continuum = text_entry.Show() == 1

# verify the render ID
album_id: str
render_id: str
if continuum:
    render_id = text_entry.Text().strip()
    continuum = len(render_id) == 6 and render_id[0].isdigit() and render_id[1].isdigit() and \
                render_id[3].isdigit() and render_id[4].isdigit() and render_id[5].isdigit() and \
                render_id[2] == '-'
    if not continuum:
        poser.DialogSimple.MessageBox('Invalid Fantasy render ID!')
    else:
        album_id = render_id[0:2]

# find the album
album_path = None
if continuum:
    gallery_path = os.path.join(os.environ['ONEDRIVE'], 'Projects', 'Fantasy')
    for album_name in os.listdir(gallery_path):
        if album_name.startswith(album_id + '. '):
            album_path = os.path.join(gallery_path, album_name)
    continuum = album_path is not None
    if not continuum:
        poser.DialogSimple.MessageBox('Album not found!')

# find the candidate archives
candidate_archives = {}
if continuum:
    archive_dir = os.path.join(album_path, 'Archive')
    for archive_name in os.listdir(archive_dir):
        if archive_name.startswith(render_id):
            candidate_archives[archive_name] = os.path.join(archive_dir, archive_name)
    continuum = len(candidate_archives) > 0
    if not continuum:
        poser.DialogSimple.MessageBox('Archive not found!')

# let the user choose which scene if necessary
archive_path = None
if continuum:
    if len(candidate_archives) == 1:
        archive_path = list(candidate_archives.values())[0]
    else:
        choice = poser.DialogSimple.AskMenu(
            f'Restore Pose', 'Which scene?:', tuple(candidate_archives.keys()))
        if choice is not None and len(choice) > 0:
            archive_path = candidate_archives[choice]
        else:
            continuum = False

# find the scene in the archive
pz3_name = None
if continuum:
    RAR = os.path.join(os.environ['PROGRAMFILES'], 'WinRAR', 'Rar.exe')
    files = subprocess.run(
        [RAR, 'lb', archive_path], capture_output=True, text=True
    ).stdout.split('\n')
    for file in files:
        if file.endswith('.pz3'):
            pz3_name = file
    continuum = pz3_name is not None
    if not continuum:
        poser.DialogSimple.MessageBox('No scenes were found in this archive!')

# extract the scene and pose
if continuum:
    figure_pose_from_scene.pose(
        pz3=subprocess.run(
            [RAR, 'p', archive_path, pz3_name], capture_output=True, text=True
        ).stdout
    )
