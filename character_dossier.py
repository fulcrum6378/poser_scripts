import os
import poser
from typing import Any, Dict, Optional

import quick_yaml


def load_dossier() -> Optional[Dict[str, Any]]:
    figure_name = poser.Scene().CurrentFigure().Name()
    # do NOT make this^ a function parameter with a default value; it'll be cached!!!
    if figure_name == 'HORN': figure_name = 'MAHDI'
    if figure_name == 'BEAST': figure_name = 'MILO'
    character = figure_name.capitalize()
    dossier_dir = os.environ['ONEDRIVE'] + rf'\Projects\Characters\{character}\Dossier'
    if not os.path.isdir(dossier_dir):
        raise Exception('This character has no dossier directory.')
    dossier_path: Optional[str] = None
    for dossier_file in os.listdir(dossier_dir).__reversed__():
        if dossier_file.endswith('.yml'):
            dossier_path = os.path.join(dossier_dir, dossier_file)
            break
    dossier = quick_yaml.load(open(dossier_path, 'r').read())
    return dossier
