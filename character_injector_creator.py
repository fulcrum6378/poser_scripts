import os
from typing import Any, Dict, Iterable, List, Optional

SCALE_MULTIPLIER = 0.01
TRANSLATION_MULTIPLIER_HIP = 0.0038149298209603575  # synchronised with Espinela's hip
TRANSLATION_MULTIPLIER_HEAD = 0.0038125


def create_injector(
        v4_sample: poser.FigureType,
        character_name: str,
        character_version: str,
        for_ds: bool,
) -> None:
    global dossier, pz2, figure_type

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

    # determine figure type
    figure_type = list(dossier['Figure'].keys())[0]
    figure_type = {
        'Victoria 4': 'Victoria 4',
        'Victoria 4.2': 'Victoria 4',
        'Michael 4': 'Michael 4',
    }[figure_type]
    if figure_type == 'Victoria 4':
        figure_type_abbr = 'V4'
    else:
        figure_type_abbr = 'M4'

    # ------------------------PYTHON SCRIPT-------------------------

    # determine the path of the auto-generated Python script for this character
    py3_name = character_name.lower() + '_v' + character_version.replace('.', '_') + '.py'
    py3_dir = os.path.join(target_library, 'Runtime', 'Python', 'poserScripts', 'Characters')
    if not os.path.isdir(py3_dir):
        os.makedirs(py3_dir)
    py3 = open(os.path.join(py3_dir, py3_name), 'w')

    # begin writing python
    print(f"""import poser

# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != '{character_name.upper()}':
    figure.SetName('{character_name.upper()}')""", file=py3)

    if 'Special' in dossier['Body'] or ('Chest' in dossier and 'Special' in dossier['Chest']):
        print("\n    body = figure.Actor('BODY')", file=py3)

    # custom body parameters and full body morphs
    if 'Special' in dossier['Body']:
        for parm in dossier['Body']['Special'].values():
            if 'IsMorphTarget' not in parm:
                print(f"    body.CreateValueParameter('{parm['Name']}')", file=py3)
            else:
                morph_target_path = os.path.join(
                    os.environ['ONEDRIVE'], 'Projects', 'Characters', character_name,
                    'Sculpture on ' + figure_type_abbr, parm['Name'] + '.obj')
                print(f"    figure.LoadFullBodyMorph(\n        r'{morph_target_path}')", file=py3)

    # custom chest morphs
    if 'Chest' in dossier and 'Special' in dossier['Chest']:
        print(f"\n    chest = figure.Actor('chest')", file=py3)
        for morph in dossier['Chest']['Special'].values():
            morph_target_path = os.path.join(
                os.environ['ONEDRIVE'], 'Projects', 'Characters', character_name,
                'Sculpture on ' + figure_type_abbr, morph['Name'] + '.obj')
            print(f"    figure.LoadFullBodyMorph(\n        r'{morph_target_path}')", file=py3)
            print(f"    body.DeleteTarget(\n        r'{morph['Name']}')", file=py3)

    # end writing python
    print("""
else:
    poser.ExecFile('../MAHDI/figure_remove_empty_daz_params_silent.py')
    poser.ExecFile('../MAHDI/character_material_loader.py')""", file=py3)

    # -------------------------POSER SCRIPT-------------------------

    # determine the path of PZ2
    pz2_dir = os.path.join(target_library, 'Runtime', 'Libraries', 'Pose', '!Characters')
    if not os.path.isdir(pz2_dir):
        os.makedirs(pz2_dir)
    pz2 = open(
        os.path.join(pz2_dir, f'{character_name} v{character_version}{"-DS" if for_ds else ""}.pz2'),
        'w', encoding='cp1252', newline='\n')

    # Poser version
    print('{\n\nversion\n	{\n	number 14\n	}\n', file=pz2)

    # primary Python script
    print('runPythonScript "Runtime:Python:poserScripts:Characters:' + py3_name + '"\n', file=pz2)

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

    # ----------------------V4/M4 Body Morphs++---------------------

    dynamic_pbms: Iterable[str] = {
        'BicepsFlex', 'CalvesFlex', 'FeetForShoe', 'GluteFlexL', 'GluteFlexR', 'Inhale', 'ToeBigCurl',
        'ToeBigSide-Side', 'ToeBigUp-Down', 'ToesPointed', 'ToesSmallIn', 'ToesSmallUp-Down'}
    if figure_type == 'Victoria 4':
        dynamic_pbms.update([
            'BreastDownL', 'BreastDownR', 'BreastInL', 'BreastInR', 'BreastOutL', 'BreastOutR',
            'BreastUpL', 'BreastUpR', 'BreastsCleavage', 'BreastsDiameter', 'BreastsDroop',
            'BreastsFlatten', 'BreastsHangForward', 'BreastsNatural', 'BreastsPerk', 'NailsLength',
            'StomachDepth'
        ])

    static_pbms: List[str] = []
    contextual_pbms: List[str] = []
    if 'Body' in dossier and 'Morphs++' in dossier['Body']:

        if 'Full Body' in dossier['Body']['Morphs++']:
            print(f'\n// {figure_type_abbr} Full Body Morphs++', file=pz2)
            for fbm in sorted(list(dossier['Body']['Morphs++']['Full Body'].keys())):
                inj_deltas('Morphs++', 'FBM', fbm)
                morphs['BODY']['FBM' + fbm] = dossier['Body']['Morphs++']['Full Body'][fbm]

        for pbm_group_name, pbm_group in dossier['Body']['Morphs++'].items():
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

    if 'Head' in dossier and 'Morphs++' in dossier['Head']:

        static_phms: List[str] = []
        contextual_phms: List[str] = []
        phm_groups = dossier['Head']['Morphs++']
        for phm_group in phm_groups.values():
            for phm, phm_node in phm_group.items():
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
    if 'Body' in dossier and 'Elite' in dossier['Body']:
        print(f'\n// {figure_type_abbr} Elite Morphs', file=pz2)
        for morph_name, morph_values in dossier['Body']['Elite'].items():
            morph_type = 'FBM' if morph_name.endswith('Body') else 'PBM'
            inj_deltas('Elite', morph_type, morph_name)
            morphs['BODY'][morph_type + morph_name] = morph_values

    # V4/M4 Stephanie Morphs
    s4_static_pbms: List[str] = []
    s4_contextual_pbms: List[str] = []
    if figure_type == 'Victoria 4':
        if 'Body' in dossier and 'Stephanie 4' in dossier['Body']:
            for pbm_group_name, pbm_group in dossier['Body']['Stephanie 4'].items():
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
    if figure_type == 'Victoria 4' and 'Body' in dossier and 'Muscle' in dossier['Body']:
        print(f'\n// V4 Muscle Morphs', file=pz2)
        for morph_name, morph_values in sorted(list(dossier['Body']['Muscle'].items())):
            inj_deltas('Muscle', 'PBM', morph_name)
        for morph_name, morph_values in dossier['Body']['Muscle'].items():
            morphs['BODY']['PBM' + morph_name] = morph_values

    # 3rd party morphs
    if 'Chest' in dossier and 'JawDropper' in dossier['Chest']:
        print('\n\n// XandM Jaw-Dropper Breast Morphs', file=pz2)
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

    # write custom body parameters
    for parm in dossier['Body']['Special'].values():
        special_parm(parm)

    # write DAZ body parameters
    body = v4_sample.Actor('BODY')
    for morph_name, morph_values in morphs['BODY'].items():
        parm = body.Parameter(morph_name)
        print(f'		{"targetGeom" if parm.IsMorphTarget() else "valueParm"} {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values)
        print('			}', file=pz2)
        if not parm.IsMorphTarget() and isinstance(morph_values, dict) and \
                (len(morph_values) > 1 or list(morph_values.keys())[0] != 'N'):
            for special_param, special_value in morph_values.items():
                if special_param == 'N': continue
                actor_name = get_actor_name_by_morph_name(morph_name)
                if morph_name not in morphs[actor_name]:
                    morphs[actor_name][morph_name] = {}
                morphs[actor_name][morph_name][special_param] = special_value

    # body scale
    print('		propagatingScale scale\n			{', file=pz2)
    tweak_parm(dossier['Body']['Scale'], SCALE_MULTIPLIER)
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
    if 'Muscle' in dossier['Body'] and 'RectusFemorus' in dossier['Body']['Muscle']:
        print('''				groupNode Muscle
					{
					collapsed 0
					}''', file=pz2)
    print('''				}
			}''', file=pz2)

    # write DAZ hip parameters
    for morph_name, morph_values in morphs['hip'].items():
        print(f'		targetGeom {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values)
        print('			}', file=pz2)

    # hip Y position
    print('		translateY ytran\n			{', file=pz2)
    tweak_parm(dossier['Hip']['yTranslate'], TRANSLATION_MULTIPLIER_HIP)
    print('			}', file=pz2)

    # end hip
    print('		}\n	}', file=pz2)

    if not for_ds or len(morphs['abdomen']) > 0 or 'Abdomen' in dossier:

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
            tweak_parm(morph_values)
            print('			}', file=pz2)

        # end abdomen
        print('		}\n	}', file=pz2)

    if len(morphs['chest']) > 0 and (not for_ds and figure_type == 'Victoria 4') or 'Chest' in dossier:

        # begin chest
        print('''
actor chest:1
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
        if 'Chest' in dossier and 'Special' in dossier['Chest']:
            print('''			groupNode Special
				{
				collapsed 1''', file=pz2)
            for parm in dossier['Chest']['Special'].values():
                print('				parmNode ' + parm['Name'], file=pz2)
            print('				}', file=pz2)
        print('''			}''', file=pz2)

        # write custom chest morphs
        if 'Chest' in dossier and 'Special' in dossier['Chest']:
            for parm in dossier['Chest']['Special'].values():
                special_parm(parm)

        # write DAZ chest parameters
        for morph_name, morph_values in morphs['chest'].items():
            print(f'		targetGeom {morph_name}', file=pz2)
            print('			{', file=pz2)
            tweak_parm(morph_values)
            print('			}', file=pz2)

        # 3rd-party morphs
        if 'Chest' in dossier and 'JawDropper' in dossier['Chest']:
            for morph_name, user_entry in dossier['Chest']['JawDropper'].items():
                print(f'		targetGeom {morph_name}', file=pz2)
                print('			{', file=pz2)
                tweak_parm(user_entry)
                print('			}', file=pz2)

        # end chest
        print('		}\n	}', file=pz2)

    if len(morphs['neck']) > 0 or 'Neck' in dossier:

        # begin neck
        print('''\nactor neck:1
    	{
    	channels
    		{''', file=pz2)

        if 'Neck' in dossier and 'Scale' in dossier['Neck']:
            print('		scale scale\n			{', file=pz2)
            tweak_parm(dossier['Neck']['Scale'], SCALE_MULTIPLIER, True)
            print('			}', file=pz2)

        # end neck
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
    head = v4_sample.Actor('head')
    for morph_name, morph_values in morphs['head'].items():
        parm = head.Parameter(morph_name)
        print(f'		{"targetGeom" if parm.IsMorphTarget() else "valueParm"} {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values)
        print('			}', file=pz2)

    if 'Scale' in dossier['Head']:
        print('		scale scale\n			{', file=pz2)
        tweak_parm(dossier['Head']['Scale'], SCALE_MULTIPLIER, True)
        print('			}', file=pz2)

    # end head
    print('		}\n	}', file=pz2)

    # eyes
    if 'Eyes' in dossier:
        for side in ['r', 'l']:
            print('''\nactor ''' + side + '''Eye:1
	{
	channels
		{''', file=pz2)

            if 'Scale' in dossier['Eyes'] or 'Scale' in dossier['Head']:
                if 'Scale' in dossier['Head']:
                    scale = dossier['Head']['Scale']
                else:
                    scale = dossier['Eyes']['Scale']

                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, True)
                print('			}', file=pz2)

            if 'yTranslate' in dossier['Eyes']:
                print('		translateY ytran\n			{', file=pz2)
                tweak_parm(dossier['Eyes']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
                print('			}', file=pz2)

            if 'zTranslate' in dossier['Eyes']:
                print('		translateZ ztran\n			{', file=pz2)
                tweak_parm(dossier['Eyes']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
                print('			}', file=pz2)

            print('''		}
	}''', file=pz2)

    # upper jaw
    if 'UpperJaw' in dossier:
        print('''\nactor upperJaw:1
	{
	channels
		{''', file=pz2)

        if 'Scale' in dossier['UpperJaw'] or 'Scale' in dossier['Head']:
            if 'Scale' in dossier['Head']:
                scale = dossier['Head']['Scale']
            else:
                scale = dossier['UpperJaw']['Scale']

            print('		scale scale\n			{', file=pz2)
            tweak_parm(scale, SCALE_MULTIPLIER, True)
            print('			}', file=pz2)

        if 'yTranslate' in dossier['UpperJaw']:
            print('		translateY ytran\n			{', file=pz2)
            tweak_parm(dossier['UpperJaw']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
            print('			}', file=pz2)

        if 'zTranslate' in dossier['UpperJaw']:
            print('		translateZ ztran\n			{', file=pz2)
            tweak_parm(dossier['UpperJaw']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
            print('			}', file=pz2)

        print('''		}
	}''', file=pz2)

    # lower jaw
    if 'LowerJaw' in dossier:
        print('''\nactor lowerJaw:1
	{
	channels
		{''', file=pz2)

        if 'Scale' in dossier['LowerJaw'] or 'Scale' in dossier['Head']:
            if 'Scale' in dossier['Head']:
                scale = dossier['Head']['Scale']
            else:
                scale = dossier['LowerJaw']['Scale']

            print('		scale scale\n			{', file=pz2)
            tweak_parm(scale, SCALE_MULTIPLIER, True)
            print('			}', file=pz2)

        if 'yTranslate' in dossier['LowerJaw']:
            print('		translateY ytran\n			{', file=pz2)
            tweak_parm(dossier['LowerJaw']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
            print('			}', file=pz2)

        if 'zTranslate' in dossier['LowerJaw']:
            print('		translateZ ztran\n			{', file=pz2)
            tweak_parm(dossier['LowerJaw']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, True)
            print('			}', file=pz2)

        print('''		}
	}''', file=pz2)

    if 'Tongue' in dossier:
        print('\n', file=pz2)
        for actor in ['tongueBase', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'tongue05', 'tongueTip']:
            print('''\nactor ''' + actor + ''':1
	{
	channels
		{''', file=pz2)

            if 'Scale' in dossier['Tongue'] or 'Scale' in dossier['Head']:
                if 'Scale' in dossier['Head']:
                    scale = dossier['Head']['Scale']
                else:
                    scale = dossier['Tongue']['Scale']

                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, True)
                print('			}', file=pz2)

            print('''		}
	}''', file=pz2)

    # arms
    for arm_side in ['r', 'l']:
        print('\n', file=pz2)

        # collars
        if 'Collars' in dossier:
            print('''
actor ''' + arm_side + '''Collar:1
	{
	channels
		{''', file=pz2)
            if not for_ds and 'Scale' in dossier['Collars']:
                print('''		groups
			{''', file=pz2)
                print('''			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 0
						}
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Collars' in dossier and 'Scale' in dossier['Shoulders']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Collars']['Scale'], SCALE_MULTIPLIER, True)
                print('			}', file=pz2)

            print('		}\n	}', file=pz2)

        # shoulders
        if not for_ds or 'Shoulders' in dossier:
            print('''
actor ''' + arm_side + '''Shldr:1
	{
	channels
		{''', file=pz2)
            if not for_ds:
                print('''		groups
			{''', file=pz2)
                if 'Shoulders' not in dossier or 'Scale' not in dossier['Shoulders']:
                    print('''			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}''', file=pz2)
                if 'BicepsFlex' in dynamic_pbms:
                    print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Shoulders' in dossier and 'Scale' in dossier['Shoulders']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Shoulders']['Scale'], SCALE_MULTIPLIER)
                print('			}', file=pz2)

            print('		}\n	}', file=pz2)

        # forearms
        if not for_ds or 'Forearms' in dossier:
            print('''
actor ''' + arm_side + '''ForeArm:1
	{
	channels
		{''', file=pz2)

            if not for_ds and ('Forearms' not in dossier or 'Scale' not in dossier['Forearms']):
                print('''		groups
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
			}''', file=pz2)

            if 'Forearms' in dossier and 'Scale' in dossier['Forearms']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Forearms']['Scale'], SCALE_MULTIPLIER)
                print('			}', file=pz2)

            print('''		}\n	}''', file=pz2)

        # hands
        if not for_ds or 'Hands' in dossier:
            print('''
actor ''' + arm_side + '''Hand:1
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

    # legs
    for leg_side in ['r', 'l']:
        print('\n', file=pz2)

        # thighs
        if not for_ds or 'Thighs' in dossier:
            print('''
actor ''' + leg_side + '''Thigh:1
	{
	channels
		{''', file=pz2)
            if not for_ds:
                print('''		groups
			{''', file=pz2)
                if 'Thighs' not in dossier or 'Scale' not in dossier['Thighs']:
                    print('''			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 1
						}
					}
				}''', file=pz2)
                if 'Muscle' in dossier['Body'] and 'VastusMedialus' in dossier['Body']['Muscle']:
                    print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Muscle
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Thighs' in dossier and 'Scale' in dossier['Thighs']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Thighs']['Scale'], SCALE_MULTIPLIER)
                print('			}', file=pz2)

            print('		}\n	}', file=pz2)

        if not for_ds or 'Shins' in dossier:
            print('''
actor ''' + leg_side + '''Shin:1
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
	}''', file=pz2)

        if not for_ds and 'Feet' in dossier:
            print('''
actor ''' + leg_side + '''Foot:1
		{
		channels
			{''', file=pz2)
            if not for_ds and 'Feet' in dossier and 'Scale' in dossier['Feet']:
                print('''		groups
			{''', file=pz2)
                if 'Feet' in dossier and 'Scale' in dossier['Feet']:
                    print('''			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 0
						}
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Feet' in dossier and 'Scale' in dossier['Feet']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, True)
                print('			}', file=pz2)

            print('		}\n	}', file=pz2)

        if not for_ds or 'Feet' in dossier or 'Toes' in dossier:
            print('''
actor ''' + leg_side + '''Toe:1
	{
	channels
		{''', file=pz2)

            scale = None
            if 'Feet' in dossier and 'Scale' in dossier['Feet']:
                scale = dossier['Feet']['Scale']
            if 'Toes' in dossier and 'Scale' in dossier['Toes']:
                scale = dossier['Toes']['Scale']

            if not for_ds:
                print('''		groups
			{''', file=pz2)

                if scale is not None:
                    print('''			groupNode General
				{
				groupNode Transforms
					{
					groupNode Scale
						{
						collapsed 0
						}
					}
				}''')

                print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if scale is not None:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, True)
                print('			}', file=pz2)

            print('		}\n	}', file=pz2)

    # figure settings
    print('''\n\n
figure
	{''', file=pz2)

    if 'Subdivision' in dossier['Figure']:
        print('	subdivLevels 0', file=pz2)
        print('	subdivRenderLevels ' + dossier['Figure']['Subdivision'], file=pz2)

    # skinning method
    print('	skinType 3', file=pz2)  # Poser Unimesh

    print('	}', file=pz2)

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


def special_parm(parm: Dict[str, Any]):
    global pz2

    init_value = '0'
    if 'Default' in parm:
        init_value = parm['Default']
    elif 'IsMorphTarget' in parm:
        init_value = '1'

    sensitivity = '0.004'
    if 'Sensitivity' in parm:
        sensitivity = parm['Sensitivity']
    elif 'IsMorphTarget' in parm:
        sensitivity = '1'

    min_val, max_val = '0', '1'
    if 'Min' in parm:
        min_val = parm['Min']
    if 'Max' in parm:
        max_val = parm['Max']

    print('''		valueParm ''' + parm['Name'] + '''
			{
			initValue ''' + init_value + '''
			min ''' + min_val + '''
			max ''' + max_val + '''
			trackingScale ''' + sensitivity + '''
			keys
				{
				k  0  ''' + init_value + '''
				}''', file=pz2)

    if 'Dependencies' in parm:
        value_ops: Dict[str, str] = {}
        for dep_abbr, dep_value in parm['Dependencies'].items():
            value_ops[dossier['Body']['Special'][dep_abbr]['Name']] = dep_value
        value_op_delta_add(value_ops, 1)

    print('			}', file=pz2)


def tweak_parm(
        user_entry: Any,
        multiplier: float = 1,
        unhide: bool = False
) -> None:
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
        print('			initValue ' + poser_float(value, multiplier), file=pz2)
    if unhide: print('			hidden 0', file=pz2)
    if value is not None:
        print('''			keys
				{
				k  0  ''' + poser_float(value, multiplier) + '''
				}''', file=pz2)
    if len(value_ops) != 0:
        value_op_delta_add(value_ops, multiplier)


def poser_float(s: str, multiplier: float) -> str:
    fl = float(s.strip()) * multiplier
    if fl % 1 == 0:
        return str(fl).split('.')[0]
    else:
        for decimals in range(4, 8):
            rounded = round(fl, decimals)
            if abs(fl - rounded) < 1e-10:  # 0.00000001
                fl = rounded
                break
        return str(fl).rstrip('0').rstrip('.')


def value_op_delta_add(value_ops: Dict[str, str], multiplier: float):
    for parm_name, parm_value in value_ops.items():
        print(f'''			valueOpDeltaAdd
				Figure 1
				BODY:1
				{parm_name}
				deltaAddDelta {value_op_number(parm_value, multiplier)}''', file=pz2)


def value_op_number(s: str, multiplier: float) -> str:
    return f'{s[-1] if s[-1] == "-" else ""}{poser_float(s.strip()[1:-2], multiplier)}'


def get_actor_name_by_morph_name(name: str) -> str:
    if name in ['PBMRectusFemorus'] or any_in_str(name, ['Glutes']):
        return 'hip'
    elif name in ['PBMBellyThin', 'PBMLineaAlba', 'PBMNavelHorizontal', 'PBMNavelSize', 'PBMNavelVertical',
                  'PBMTummyOut', 'PBMWaistWidth']:
        return 'abdomen'
    elif name in ['PBMInhale', 'PBMTrapsSize'] or \
            any_in_str(name, ['Breast', 'Areola', 'Nipple']):
        return 'chest'
    else:
        raise Exception(f'What actor does this morph belong to? {name}')


def any_in_str(string: str, list: List[str]) -> bool:
    for i in list:
        if i in string:
            return True
    return False


if __name__ == '__main__':
    continuum = True

    figure = poser.Scene().CurrentFigure()
    if figure is None or 'blMil' not in figure.GeomFileName():
        poser.DialogSimple.MessageBox('Please load and select a V4/M4 figure as a sample.')
        continuum = False

    if continuum:
        file_chooser = poser.DialogFileChooser(
            poser.kDialogFileChooserOpen, None, f'Select a Dossier file (*.YML)')
        continuum = file_chooser.Show()

    if continuum:
        import quick_yaml

        dossier_path = file_chooser.Path()
        dossier = quick_yaml.load(open(dossier_path, 'r').read())
        dossier_name_split = os.path.basename(dossier_path).rsplit('.', 1)[0].split(' v')
        create_injector(
            figure,
            dossier_name_split[0],
            dossier_name_split[1].split(' ')[0],
            poser.DialogSimple.YesNo('Select Yes for Poser\nNo for DAZ Studio') != 1)
