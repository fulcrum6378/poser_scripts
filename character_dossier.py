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

    # find the dossier directory
    dossier_dir = os.path.join(
        os.environ['ONEDRIVE'], 'Projects', 'Characters', figure_name.capitalize(), 'Dossier')
    if not os.path.isdir(dossier_dir):
        raise Exception('This character has no dossier directory.')

    # find the right dossier
    dossier_path: Optional[str] = None
    if version is None:
        for dossier_file in os.listdir(dossier_dir).__reversed__():
            if dossier_file.endswith('.yml'):
                dossier_path = os.path.join(dossier_dir, dossier_file)
                break
    else:
        dossier_path = os.path.join(dossier_dir, f'{figure_name.capitalize()} v{version} - {revision}.yml')

    # load the dossier
    if dossier_path is None:
        raise Exception('Could not find a dossier file!')
    dossier = quick_yaml.load(open(dossier_path, 'r').read())
    return dossier
