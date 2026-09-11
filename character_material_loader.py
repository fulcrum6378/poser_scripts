import os
import poser
from typing import Optional

import quick_yaml
from v4_material_loader import inject_material

scene = poser.Scene()
figure = scene.CurrentFigure()
figure_name = figure.Name()
if figure_name == 'HORN': figure_name = 'MAHDI'
if figure_name == 'BEAST': figure_name = 'MILO'
character = figure_name.capitalize()
dossier_dir = os.environ['ONEDRIVE'] + rf'\Projects\Characters\{character}\Dossier'
if not os.path.isdir(dossier_dir):
    raise Exception('This character has no dossier directory.')
manifest_path: Optional[str] = None
for dossier_file in os.listdir(dossier_dir).__reversed__():
    if dossier_file.endswith('.yml'):
        manifest_path = os.path.join(dossier_dir, dossier_file)
        break
manifest = quick_yaml.load(open(manifest_path, 'r').read())

for mat in figure.Materials():
    inject_material(mat)
