import math
import os
import subprocess
from typing import List
from datetime import datetime

import poser

import quick_yaml

DESKTOP = os.environ['USERPROFILE'] + '\\Desktop'
RENDER_CACHE_1 = DESKTOP
RENDER_CACHE_2 = '\\\\NERA\\Renders'
POWERSHELL = r'C:\Program Files\PowerShell\7\pwsh.exe'

scene_path: str = poser.Scene().DocumentPath()
album_path: str = os.path.dirname(scene_path)
if os.path.basename(album_path) == 'Templates':
    album_path = os.path.dirname(album_path)
render_cache = RENDER_CACHE_2
continuum: bool = os.path.basename(album_path)[2:4] == '. '

# check if this is a Fantasy scene first
album_id: str = ''
album_name: str = ''
if not continuum:
    poser.DialogSimple.MessageBox('This document is not a Fantasy scene.')
else:
    album_id, album_name = os.path.basename(album_path).split('. ')

# determine the render cache directory
if continuum:
    have_laptop_render = False
    for file in os.listdir(RENDER_CACHE_1):
        if file.endswith('.exr') and \
                os.path.getsize(os.path.join(RENDER_CACHE_1, file)) > 104_857_600:  # 100 MB
            have_laptop_render = True
    if have_laptop_render:
        if poser.DialogSimple.YesNo('Is it rendered in this device?') == 1:
            render_cache = RENDER_CACHE_1

# let the user choose a render from the render cache
renders: List[str]
if continuum:
    renders = []
    for render in os.listdir(render_cache):
        if not render.endswith('.exr'): continue
        renders.append(render.rsplit('.', 1)[0])
    choice = poser.DialogSimple.AskMenu('Fantasy Register Render', 'Choose a render:', tuple(renders))
    continuum = choice is not None and len(choice) > 0

if continuum:
    #
    # catalogue this render in the YML file of its album
    yml = os.path.join(album_path, album_name + '.yml')
    exr_path = render_cache + '\\' + choice + '.exr'
    if os.path.isfile(yml):
        render_name = list(quick_yaml.load(open(yml, 'r').read()).keys())[-1]
        render_id = int(render_name.split('. ')[0]) + 1
    else:
        render_id = 1
    render_id = f'{render_id:03d}'
    export_name = album_id + '-' + render_id
    dt = choice
    n = lambda s: int(s.strip())
    start_time = datetime(n(dt[0:4]), n(dt[5:7]), n(dt[8:10]), n(dt[11:13]), n(dt[14:16]), n(dt[17:19]))
    finish_time = os.path.getmtime(exr_path)
    dt_format = '%Y/%m/%d %H:%M:%S'
    open(yml, 'a').write(
        f'- {render_id}:\n'
        f'  - {start_time.strftime(dt_format)} - [{math.trunc(start_time.timestamp())}]\n'
        f'  - {datetime.fromtimestamp(finish_time).strftime(dt_format)} - [{math.trunc(finish_time)}]\n')

    # archive the scene
    if poser.DialogSimple.YesNo('Archive the scene?') == 1:
        archive_dir = os.path.join(album_path, 'Archive')
        if not os.path.isdir(archive_dir):
            os.mkdir(archive_dir)
        command = [os.path.join(os.environ['PROGRAMFILES'], 'WinRAR', 'Rar.exe'), 'a',
                   os.path.join(archive_dir, export_name + '.rar'),
                   os.path.basename(scene_path)]
        pmd_path = scene_path.replace('.pz3', '.pmd')
        if os.path.isfile(pmd_path):
            command.append(os.path.basename(pmd_path))
        subprocess.run(command, cwd=album_path)

    # extract poses
    if poser.DialogSimple.YesNo('Extract the poses?') == 1:
        from fantasy_extract_poses import get_pose_dir
        from fantasy_extract_poses_pz3 import extract_all

        pose_dir = get_pose_dir(album_id, album_name)
        characters = extract_all(scene_path, pose_dir, album_id, render_id)

        # create reminding shortcuts for every pose in the desktop
        for char in characters:
            command = rf'''
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("{DESKTOP}\{export_name} ({char}).lnk")
$shortcut.TargetPath = "{pose_dir}\{export_name} ({char}).pz2"
$shortcut.Save()
            '''
            subprocess.run([POWERSHELL, '-NoProfile', '-Command', command], text=True)

    # create a reminding shortcut for cropping special thumbnails for the extracted poses
    command = rf'''
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("{DESKTOP}\{export_name}.lnk")
$shortcut.TargetPath = "%ProgramFiles%\Adobe\Adobe Photoshop CS6 (64 Bit)\Photoshop.exe"
$shortcut.Arguments = "R:\Fantasy Renders\{export_name}.png"
$shortcut.WorkingDirectory = "{DESKTOP}"
$shortcut.IconLocation = "%ProgramFiles%\Adobe\Adobe Photoshop CS6 (64 Bit)\Photoshop.exe,36"
$shortcut.Save()
    '''
    subprocess.run([POWERSHELL, '-NoProfile', '-Command', command], text=True)
