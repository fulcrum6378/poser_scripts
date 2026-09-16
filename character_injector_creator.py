import os
from typing import Any, Iterable, List, Optional

import character_dossier

import importlib

importlib.reload(character_dossier)


def create_injector(
        version: Optional[str],
        revision: Optional[int],
        for_ds: bool,
) -> None:
    global dossier, pz2, figure_type

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
        'Michael 4': 'Michael 4',
    }[figure_type]

    # begin writing
    print('{\n\nversion\n	{\n	number 14\n	}\n', file=pz2)
    print('runPythonScript "Runtime:Python:poserScripts:MAHDI:_' + figure_name.lower() + '_v' + \
          version.replace('.', '_') + '.py"', file=pz2)
    print('', file=pz2)
    morphs: Dict[str, Dict[str, Any]] = {
        'BODY': {},
        'hip': {},
        'abdomen': {},
        'chest': {},
        'neck': {},
        'head': {},
    }

    # V4/M4 Base Morphs
    if figure_type == 'Victoria 4':
        print('\n// Remove V4 Base Male Morphs', file=pz2)
        rem_deltas('Base', 'DST', 'Strength')
        rem_deltas('Base', 'FBM', 'Male')
        rem_deltas('Base', 'FBM', 'MaleNS')
        rem_deltas('Base', 'FHM', 'George')
        rem_deltas('Base', 'FHM', 'John')
        rem_deltas('Base', 'FHM', 'Paul')
        figure_type_abbr = 'V4'
    else:
        figure_type_abbr = 'M4'

    # ----------------------V4/M4 Body Morphs++---------------------

    dynamic_pbms: Iterable[str] = {
        'BicepsFlex', 'CalvesFlex', 'FeetForShoe', 'GluteFlexL', 'GluteFlexR', 'Inhale', 'ToeBigCurl',
        'ToeBigSide-Side', 'ToeBigUp-Down', 'ToesPointed', 'ToesSmallIn', 'ToesSmallUp-Down'}
    if figure_type == 'Victoria 4':
        dynamic_pbms.update([
            'BreastDownL', 'BreastDownR', 'BreastInL', 'BreastInR', 'BreastOutL', 'BreastOutR',
            'BreastUpL', 'BreastUpR', 'BreastsCleavage', 'BreastsDiameter', 'BreastsDroop',
            'BreastsFlatten', 'BreastsHangForward', 'BreastsNatural', 'BreastsPerk',  # 'NailsLength',
            'StomachDepth'
        ])

    static_pbms: List[str] = []
    contextual_pbms: List[str] = []
    if 'Body' in dossier and 'Morphs | Shapes' in dossier['Body'] and \
            'Morphs++' in dossier['Body']['Morphs | Shapes']:

        if 'Full Body' in dossier['Body']['Morphs | Shapes']['Morphs++']:
            print(f'\n// {figure_type_abbr} Full Body Morphs++', file=pz2)
            for fbm in sorted(list(dossier['Body']['Morphs | Shapes']['Morphs++']['Full Body'].keys())):
                inj_deltas('Morphs++', 'FBM', fbm)
                morphs['BODY']['FBM' + fbm] = dossier['Body']['Morphs | Shapes']['Morphs++']['Full Body'][fbm]

        for pbm_group_name, pbm_group in dossier['Body']['Morphs | Shapes']['Morphs++'].items():
            if pbm_group_name == 'Full Body': continue
            for pbm, pbm_node in pbm_group.items():
                if isinstance(pbm_node, dict) and 'N' not in pbm_node.keys():
                    contextual_pbms.append(pbm)
                else:
                    static_pbms.append(pbm)
                morphs['BODY']['PBM' + pbm] = pbm_node
                if pbm in dynamic_pbms:
                    dynamic_pbms.remove(pbm)

    if len(static_pbms) != 0:
        print(f'\n// {figure_type_abbr} Partial Body Morphs++ (static)', file=pz2)
        static_pbms.sort()
        for pbm in static_pbms:
            inj_deltas('Morphs++', 'PBM', pbm)

    if len(contextual_pbms) != 0:
        print(f'\n// {figure_type_abbr} Partial Body Morphs++ (contextual)', file=pz2)
        contextual_pbms.sort()
        for pbm in contextual_pbms:
            inj_deltas('Morphs++', 'PBM', pbm)

    dynamic_pbms = sorted(list(dynamic_pbms))
    if len(dynamic_pbms) != 0:
        print(f'\n// {figure_type_abbr} Partial Body Morphs++ (dynamic)', file=pz2)
        for pbm in dynamic_pbms:
            inj_deltas('Morphs++', 'PBM', pbm)

    # ----------------------V4/M4 Head Morphs++---------------------

    if 'Head' in dossier and 'Morphs | Shapes' in dossier['Head'] and \
            'Morphs++' in dossier['Head']['Morphs | Shapes']:

        static_phms: List[str] = []
        contextual_phms: List[str] = []
        phm_groups = dossier['Head']['Morphs | Shapes']['Morphs++']
        # if 'Eyes' in dossier['Head']['Morphs | Shapes']['Morphs++'] and \
        #        'Eyeballs' in dossier['Head']['Morphs | Shapes']['Morphs++']['Eyes']:
        #    phm_groups['Eyeballs'] = dossier['Head']['Morphs | Shapes']['Morphs++']['Eyes']['Eyeballs']
        for phm_group in phm_groups.values():
            for phm, phm_node in phm_group.items():
                # if phm == 'Eyeballs': continue
                if isinstance(phm_node, dict) and 'N' not in phm_node.keys():
                    contextual_phms.append(phm)
                else:
                    static_phms.append(phm)
                morphs['head']['PHM' + phm] = phm_node

        if len(static_phms) != 0:
            print('\n// V4 Partial Head Morphs++ (static)', file=pz2)
            static_phms.sort()
            for phm in static_phms:
                inj_deltas('Morphs++', 'PHM', phm)

        if len(contextual_phms) != 0:
            print('\n// V4 Partial Head Morphs++ (contextual)', file=pz2)
            contextual_phms.sort()
            for phm in contextual_phms:
                inj_deltas('Morphs++', 'PHM', phm)

    # V4/M4 Control Morphs++
    print(f'\n// {figure_type_abbr} Control Morphs++', file=pz2)
    for ctrl in [
        'ArmsFront-Back', 'ArmsUp-Down', 'EyesSide-Side', 'EyesUp-Down', 'HandGrasp', 'HandSpread',
        'IndexGrasp', 'lArmDown', 'lArmUp', 'MiddleGrasp', 'NeckHeadBend', 'NeckHeadSide-Side',
        'NeckHeadTwist', 'PinkyGrasp', 'rArmDown', 'rArmUp', 'RingGrasp', 'ShoulderShrug', 'ThumbGrasp',
        'TorsoBend', 'TorsoSide-Side', 'TorsoTwist', 'WaistBend', 'WaistBendBack', 'WaistBendFront']:
        inj_deltas('Morphs++', 'CTRL', ctrl)

    # V4/M4 Elite Morphs
    if 'Body' in dossier and 'Morphs | Shapes' in dossier['Body'] and \
            'Elite' in dossier['Body']['Morphs | Shapes']:
        print(f'\n// {figure_type_abbr} Elite Morphs', file=pz2)
        for morph_name, morph_values in dossier['Body']['Morphs | Shapes']['Elite'].items():
            morph_type = 'FBM' if morph_name.endswith('Body') else 'PBM'
            inj_deltas('Elite', morph_type, morph_name)
            morphs['BODY'][morph_type + morph_name] = morph_values

    # V4/M4 Stephanie Morphs
    s4_static_pbms: List[str] = []
    s4_contextual_pbms: List[str] = []
    if figure_type == 'Victoria 4':
        if 'Body' in dossier and 'Morphs | Shapes' in dossier['Body'] and \
                'Stephanie 4' in dossier['Body']['Morphs | Shapes']:
            for pbm_group_name, pbm_group in dossier['Body']['Morphs | Shapes']['Stephanie 4'].items():
                if pbm_group_name == 'Full Body': continue
                for pbm, pbm_node in pbm_group.items():
                    if isinstance(pbm_node, dict) and 'N' not in pbm_node.keys():
                        s4_contextual_pbms.append(pbm)
                    else:
                        s4_static_pbms.append(pbm)
                    morphs['BODY']['PBM' + pbm] = pbm_node
        if 'PubicDepth' not in s4_static_pbms and 'PubicDepth' not in s4_contextual_pbms:
            s4_contextual_pbms.append('PubicDepth')

        if len(s4_static_pbms) != 0:
            print(f'\n// Stephanie 4 Morphs (static)', file=pz2)
            s4_static_pbms.sort()
            for pbm in s4_static_pbms:
                inj_deltas('Stephanie 4', 'PBM', pbm)

        if len(s4_contextual_pbms) != 0:
            print(f'\n// Stephanie 4 Morphs (contextual)', file=pz2)
            s4_contextual_pbms.sort()
            for pbm in s4_contextual_pbms:
                inj_deltas('Stephanie 4', 'PBM', pbm)

    # V4 Muscle Morphs
    if figure_type == 'Victoria 4' and 'Body' in dossier and 'Morphs | Shapes' in dossier['Body'] and \
            'Muscle' in dossier['Body']['Morphs | Shapes']:
        print(f'\n// V4 Muscle Morphs', file=pz2)
        for morph_name, morph_values in dossier['Body']['Morphs | Shapes']['Muscle'].items():
            inj_deltas('Muscle', 'PBM', morph_name)
            morphs['BODY']['PBM' + morph_name] = morph_values
    print('', file=pz2)

    if 'XandM Jaw-dropper Breast Morphs' in dossier['Figure']:
        print('\n// XandM Jaw-Dropper Breast Morphs', file=pz2)
        if not for_ds:
            print('readScript "Runtime:Libraries:Pose:XandM Curves+:Breast Morphs_Jaw-dropper:'
                  '!INJ JawDropper Breast Morphs.pz2"', file=pz2)
        else:
            print('readScript "Runtime:Libraries:Pose:XandM Curves+:Breast Morphs_Jaw-dropperDAZ:'
                  '!!JawDropper Pre-Inject.pz2"', file=pz2)
            print('readScript "Runtime:Libraries:Pose:XandM Curves+:Breast Morphs_Jaw-dropperDAZ:'
                  '!INJ JawDropper Breast Morphs.pz2"', file=pz2)

    # begin BODY
    print('''\n\n
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
    if 'Special' in dossier['Body']:
        print('			groupNode Special\n				{', file=pz2)
        for parm in dossier['Body']['Special'].values():
            print('				parmNode ' + parm['Name'], file=pz2)
    print('				}', file=pz2)
    print('			}', file=pz2)

    # write DAZ body parameters
    body = figure.Actor('BODY')
    for morph_name, morph_values in morphs['BODY'].items():
        parm = body.Parameter(morph_name)
        print(f'		{"targetGeom" if parm.IsMorphTarget() else "valueParm"} {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, 1)
        print('			}', file=pz2)
        if not parm.IsMorphTarget() and isinstance(morph_values, dict) and \
                (len(morph_values) > 1 or list(morph_values.keys())[0] != 'N'):
            for special_parm, special_value in morph_values.items():
                if special_parm == 'N': continue
                actor_name = get_actor_name_by_morph_name(morph_name)
                if morph_name not in morphs[actor_name]:
                    morphs[actor_name][morph_name] = {}
                morphs[actor_name][morph_name][special_parm] = special_value

    # write custom body parameters
    for parm in dossier['Body']['Special'].values():
        print('''		valueParm ''' + parm['Name'] + '''
			{
			name ''' + parm['Name'] + '''
			initValue ''' + (parm['Default'] if 'Default' in parm else '0') + '''
			hidden 0
			enabled 1
			forceLimits 1
			min ''' + (parm['Min'] if 'Min' in parm else '0') + '''
			max ''' + (parm['Max'] if 'Max' in parm else '1') + '''
			trackingScale ''' + (parm['TrackingScale'] if 'TrackingScale' in parm else '0.004') + '''
			masterSynched 0
			keys
				{
				static  0
				k  0  ''' + (parm['Default'] if 'Default' in parm else '0') + '''
				}
			interpStyleLocked 0
			}''', file=pz2)

    # body scale
    print('		propagatingScale scale\n			{', file=pz2)
    tweak_parm(dossier['Body']['Scale'], 0.01)
    print('			}', file=pz2)

    # end BODY
    print('''		propagatingScaleX xScale
			{
			hidden 1
			}
		propagatingScaleY yScale
			{
			hidden 1
			}
		propagatingScaleZ zScale
			{
			hidden 1
			}
		}
	}''', file=pz2)

    # begin hip
    print('''\n\n
actor hip:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}''', file=pz2)
    if 'PubicDepth' in s4_contextual_pbms:
        print('''				groupNode Stephanie 4
					{
					collapsed 0
					}''', file=pz2)
    print('''				}
			}''', file=pz2)

    # write DAZ hip parameters
    for morph_name, morph_values in morphs['hip'].items():
        print(f'		targetGeom {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, 1)
        print('			}', file=pz2)

    # hip Y position
    print('		translateY ytran\n			{', file=pz2)
    tweak_parm(dossier['Hip']['yTranslate'], 0.0038149297967307)
    print('			}', file=pz2)

    # end hip
    print('		}\n	}', file=pz2)

    # begin abdomen
    print('''
actor abdomen:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}''', file=pz2)

    # write DAZ chest parameters
    for morph_name, morph_values in morphs['abdomen'].items():
        print(f'		targetGeom {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, 1)
        print('			}', file=pz2)

    # end abdomen
    print('		}\n	}', file=pz2)

    # begin chest
    print('''\nactor chest:1
	{
	channels
		{
		groups
			{''', file=pz2)
    if figure_type == 'Victoria 4':
        print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
    print('''			}''', file=pz2)

    # write DAZ chest parameters
    for morph_name, morph_values in morphs['chest'].items():
        print(f'		targetGeom {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, 1)
        print('			}', file=pz2)

    # end chest
    print('		}\n	}', file=pz2)

    # begin head
    print('''\n\n
actor head:1
	{
	channels
		{
		groups
			{
			groupNode Morphs | Expressions
				{
				collapsed 0
				groupNode Base
					{
					collapsed 0
					}
				}
			groupNode Morphforms
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}''', file=pz2)

    # write DAZ head parameters
    head = figure.Actor('head')
    for morph_name, morph_values in morphs['head'].items():
        parm = head.Parameter(morph_name)
        print(f'		{"targetGeom" if parm.IsMorphTarget() else "valueParm"} {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, 1)
        print('			}', file=pz2)

    # end head
    print('		}\n	}', file=pz2)

    # begin arms
    for side in ['r', 'l']:
        print('''\n\n
actor ''' + side + '''Shldr:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}
		}
	}

actor ''' + side + '''ForeArm:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			}
		}
	}

actor ''' + side + '''Hand:1
	{
	channels
		{
		groups
			{
			groupNode Morphforms
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}
		}
	}''', file=pz2)

    # begin legs
    for side in ['r', 'l']:
        print('''\n\n
actor ''' + side + '''Thigh:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			}
		}
	}

actor ''' + side + '''Shin:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}
		}
	}

actor ''' + side + '''Toe:1
	{
	channels
		{
		groups
			{
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}
		}
	}''', file=pz2)

    # end writing
    print('\n}', file=pz2)
    pz2.close()


def inj_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:InjDeltas.{type}{name}.pz2"',
          file=pz2)


def rem_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:RemDeltas.{type}{name}.pz2"',
          file=pz2)


def tweak_parm(user_entry: Any, multiplier: float = 1) -> None:
    global dossier, pz2, dossier

    value = None
    value_ops = {}
    if isinstance(user_entry, dict):
        for k, v in user_entry.items():
            if k == 'N':
                value = user_entry['N']
            else:
                value_ops[dossier['Body']['Special'][k]['Name']] = v
    else:
        value = user_entry

    if value is not None:
        print('''			initValue ''' + poser_float(value, multiplier) + '''
			keys
				{
				k  0  ''' + poser_float(value, multiplier) + '''
				}''', file=pz2)
    if len(value_ops) != 0:
        for k, v in value_ops.items():
            print(f'''			valueOpDeltaAdd
				Figure 1
				BODY:1
				{k}
				deltaAddDelta {value_op_number(v, multiplier)}''', file=pz2)


def poser_float(s: str, multiplier: float) -> str:
    fl = float(s.strip()) * multiplier
    if fl % 1 == 0:
        return str(fl).split('.')[0]
    else:
        return str(fl)


def value_op_number(s: str, multiplier: float) -> str:
    return f'{s[-1] if s[-1] == "-" else ""}{poser_float(s.strip()[1:-2], multiplier)}'


def get_actor_name_by_morph_name(morph_name: str) -> str:
    if any_in_str(morph_name, ['Glutes']):
        return 'hip'
    elif morph_name in ['PBMWaistWidth', 'PBMLineaAlba']:
        return 'abdomen'
    elif any_in_str(morph_name, ['Breast', 'Areola', 'Nipple']):
        return 'chest'
    else:
        raise Exception(f'What actor does this morph belong to? {morph_name}')


def any_in_str(string: str, list: List[str]) -> bool:
    for i in list:
        if i in string:
            return True
    return False


if __name__ == '__main__':
    create_injector('4.6', 4, False)
