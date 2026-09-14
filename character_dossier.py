import os
import poser
from typing import Any, Dict, Optional

import quick_yaml


def load_dossier(
        figure_name: str,
        version: Optional[str],
        revision: Optional[int],
        # never use default values in Poser scripts
) -> Optional[Dict[str, Any]]:
    if figure_name == 'HORN': figure_name = 'MAHDI'
    if figure_name == 'BEAST': figure_name = 'MILO'
    character = figure_name.capitalize()
    dossier_dir = os.environ['ONEDRIVE'] + rf'\Projects\Characters\{character}\Dossier'
    if not os.path.isdir(dossier_dir):
        raise Exception('This character has no dossier directory.')

    dossier_path: Optional[str] = None
    if version is None:
        for dossier_file in os.listdir(dossier_dir).__reversed__():
            if dossier_file.endswith('.yml'):
                dossier_path = os.path.join(dossier_dir, dossier_file)
                break
    else:
        dossier_path = os.path.join(dossier_dir, f'{character} v{version} - {revision}.yml')

    if dossier_path is None:
        raise Exception('Could not find a dossier file!')
    dossier = quick_yaml.load(open(dossier_path, 'r').read())
    return dossier
