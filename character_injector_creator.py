import os
from typing import Optional

import character_dossier

import importlib

importlib.reload(character_dossier)


def create_injector(
        version: Optional[str],
        revision: Optional[int],
        for_ds: bool,
) -> None:
    global pz2, figure_type

    scene = poser.Scene()
    figure = scene.CurrentFigure()
    figure_name = figure.Name()
    dossier = character_dossier.load_dossier(figure_name, version, revision)
    if dossier is None:
        raise Exception('This figure has no dossier!')

    # determine the libraries
    source_library: Optional[str] = None
    target_library: Optional[str] = None
    for library in poser.Libraries():
        if os.path.isdir(os.path.join(library, 'Runtime', 'Libraries', '!DAZ')):
            source_library = library
        if 'OneDrive' in library:
            target_library = library
    if source_library is None:
        raise Exception('No library was found with DAZ morphs!')
    elif target_library is None:
        target_library = source_library

    # determine the path of PZ2
    pz2_dir = os.path.join(target_library, 'Runtime', 'Libraries', 'Pose', '!' + figure_name)
    if not os.path.isdir(pz2_dir):
        os.makedirs(pz2_dir)
    pz2_path = os.path.join(pz2_dir, 'Test.pz2')
    pz2 = open(pz2_path, 'w', encoding='cp1252', newline='\n')

    # determine figure type
    figure_type = list(dossier['Figure'].keys())[0]
    figure_type = {
        'Victoria 4': 'Victoria 4',
        'Victoria 4.2': 'Victoria 4',
    }[figure_type]

    # begin writing
    print('{\n\nversion\n	{\n	number 14\n	}\n', file=pz2)
    print('runPythonScript "Runtime:Python:poserScripts:MAHDI:_' + figure_name.lower() + '_v' + \
          version.replace('.', '_') + '.py"', file=pz2)
    print('\n', file=pz2)

    if figure_type == 'Victoria 4':
        print('// Remove V4 Base Male Morphs', file=pz2)
        include_daz_pz2('Base', 'DST', 'Strength', True)
        include_daz_pz2('Base', 'FBM', 'Male', True)
        include_daz_pz2('Base', 'FBM', 'MaleNS', True)
        include_daz_pz2('Base', 'FHM', 'George', True)
        include_daz_pz2('Base', 'FHM', 'John', True)
        include_daz_pz2('Base', 'FHM', 'Paul', True)
        print('', file=pz2)

    # end writing
    print('}', file=pz2)
    pz2.close()


def include_daz_pz2(group: str, type: str, name: str, remove: bool) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:'
          f'{"InjDeltas" if not remove else "RemDeltas"}.{type}{name}.pz2"', file=pz2)


if __name__ == '__main__':
    create_injector('4.6', 4, False)
