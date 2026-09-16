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
    dossier_dir = get_dossier_dir(figure_name)
    if not os.path.isdir(dossier_dir):
        raise Exception('This character has no dossier directory.')

    dossier_path: Optional[str]
    if version is None:
        dossier_path = get_latest_dossier_path(figure_name)
    else:
        dossier_path = os.path.join(dossier_dir, f'{figure_name.capitalize()} v{version} - {revision}.yml')

    if dossier_path is None:
        raise Exception('Could not find a dossier file!')
    dossier = quick_yaml.load(open(dossier_path, 'r').read())
    return dossier


def get_dossier_dir(figure_name: str) -> str:
    return os.environ['ONEDRIVE'] + rf'\Projects\Characters\{figure_name.capitalize()}\Dossier'


def get_latest_dossier_path(figure_name: str) -> Optional[str]:
    dossier_dir = get_dossier_dir(figure_name)
    for dossier_file in os.listdir(dossier_dir).__reversed__():
        if dossier_file.endswith('.yml'):
            return os.path.join(dossier_dir, dossier_file)
    return None


def get_version_from_dossier_path(path: str) -> str:
    return os.path.basename(path).rsplit('.', 1)[0].split(' v')[1].split(' ')[0]
