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
    pz2_path = os.path.join(pz2_dir, f'Test{"-DS" if for_ds else ""}.pz2')
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
        rem_deltas('Base', 'DST', 'Strength')
        rem_deltas('Base', 'FBM', 'Male')
        rem_deltas('Base', 'FBM', 'MaleNS')
        rem_deltas('Base', 'FHM', 'George')
        rem_deltas('Base', 'FHM', 'John')
        rem_deltas('Base', 'FHM', 'Paul')
        print('', file=pz2)

    print('// V4 Control Morphs++', file=pz2)
    for ctrl in [
        'ArmsFront-Back', 'ArmsUp-Down', 'EyesSide-Side', 'EyesUp-Down', 'HandGrasp', 'HandSpread',
        'IndexGrasp', 'lArmDown', 'lArmUp', 'MiddleGrasp', 'NeckHeadBend', 'NeckHeadSide-Side',
        'NeckHeadTwist', 'PinkyGrasp', 'rArmDown', 'rArmUp', 'RingGrasp', 'ShoulderShrug', 'ThumbGrasp',
        'TorsoBend', 'TorsoSide-Side', 'TorsoTwist', 'WaistBend', 'WaistBendBack', 'WaistBendFront']:
        inj_deltas('Morphs++', 'CTRL', ctrl)
    print('', file=pz2)

    # begin BODY
    print('''

actor BODY:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Rotation
						{
						collapsed 0
						}
					groupNode Scale
						{
						collapsed 0
						}
					}
				}
			groupNode Morphforms
				{
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
    # TODO Special if exists
    print('\n			}', file=pz2)

    # end BODY
    print('''		}
	}
''', file=pz2)

    # end writing
    print('}', file=pz2)
    pz2.close()


def inj_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:InjDeltas.{type}{name}.pz2"',
          file=pz2)


def rem_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:RemDeltas.{type}{name}.pz2"',
          file=pz2)


if __name__ == '__main__':
    create_injector('4.6', 4, False)
