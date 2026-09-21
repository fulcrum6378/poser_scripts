import os
import shutil
from typing import Any, Dict, Iterable, List, Optional

POSER_VERSION = 14
PZ2_DIR_NAME = 'Characters'

SCALE_MULTIPLIER = 0.01
TRANSLATION_MULTIPLIER_HIP = 0.0038149298209603575
TRANSLATION_MULTIPLIER_HEAD = 0.0038125


def create_injector(
        v4_sample: poser.FigureType,
        character_name: str,
        character_version: str,
        for_ds: bool,
) -> None:
    global dossier, py3, pz2, figure_type, figure_type_abbr, penis

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
    penis = None

    # ------------------------PYTHON SCRIPT-------------------------

    # determine the path of the auto-generated Python script for this character
    py3_name = character_name.lower() + '_v' + character_version.replace('.', '_') + '.py'
    py3_dir = os.path.join(target_library, 'Runtime', 'Python', 'poserScripts', 'Characters')
    if not os.path.isdir(py3_dir):
        os.makedirs(py3_dir)
    py3 = open(os.path.join(py3_dir, py3_name), 'w')
    write_python_script_header(character_name)

    if 'Special' in dossier['Body'] or ('Chest' in dossier and 'Special' in dossier['Chest']):
        print("\n    body = figure.Actor('BODY')", file=py3)

    # custom body parameters and full body morphs
    special_morph_injectors: List[str] = []
    if 'Special' in dossier['Body']:
        for parm in dossier['Body']['Special'].values():
            if 'MorphTarget' not in parm:
                print(f"    body.CreateValueParameter('{parm['Name']}')", file=py3)
            else:
                morph_obj = morph_target_path(character_name, parm['Name'], 'obj')
                morph_pz2 = morph_target_path(character_name, parm['Name'], 'pz2')
                if os.path.isfile(morph_obj):
                    print(f"    figure.LoadFullBodyMorph(\n        r'{morph_obj}')", file=py3)
                elif os.path.isfile(morph_pz2):
                    special_morph_injectors.append(morph_pz2)
                else:
                    raise Exception(f'Morph file not found either in OBJ or PZ2: {morph_obj}')

    # custom chest morphs
    if 'Chest' in dossier and 'Special' in dossier['Chest']:
        print(f"\n    chest = figure.Actor('chest')", file=py3)
        for morph in dossier['Chest']['Special'].values():
            morph_obj = morph_target_path(character_name, morph['Name'], 'obj')
            print(f"    figure.LoadFullBodyMorph(\n        r'{morph_obj}')", file=py3)
            print(f"    body.DeleteTarget('{morph['Name']}')", file=py3)

    print('\nelse:', file=py3)
    write_python_script_footer()
    py3.close()

    # -------------------------POSER SCRIPT-------------------------

    # determine the path of PZ2
    pz2_dir = os.path.join(target_library, 'Runtime', 'Libraries', 'Pose', PZ2_DIR_NAME)
    if not os.path.isdir(pz2_dir):
        os.makedirs(pz2_dir)
    pz2 = open(
        os.path.join(pz2_dir, f'{character_name} v{character_version}{"-DS" if for_ds else ""}.pz2'),
        'w', encoding='cp1252', newline='\n')
    write_poser_script_header()

    # primary Python script
    print('runPythonScript "Runtime:Python:poserScripts:Characters:' + py3_name + '"', file=pz2)

    # special morph injectors
    for morph_pz2_src in special_morph_injectors:
        morph_pmd_src = morph_pz2_src[:-3] + 'pmd'
        morph_pz2 = os.path.join(pz2_dir, os.path.basename(morph_pz2_src))
        morph_pmd = os.path.join(pz2_dir, os.path.basename(morph_pmd_src))
        shutil.copy2(morph_pz2_src, morph_pz2)
        if os.path.isfile(morph_pmd_src):
            shutil.copy2(morph_pmd_src, morph_pmd)
        print(f'readScript {os.path.basename(morph_pz2)}', file=pz2)

    print('', file=pz2)

    morphs: Dict[str, Dict[str, Any]] = {
        'BODY': {},
        'hip': {},
        'abdomen': {},
        'chest': {},
        'neck': {},
        'head': {},
    }
    hide_morphs: Dict[str, List[str]] = {
        'chest': [],
        'neck': [],
        'head': [],
        'rCollar': [],
        'lCollar': [],
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

    is_always_thin = False
    is_never_muscular = figure_type == 'Victoria 4'
    if 'Body' in dossier and 'Morphs++' in dossier['Body'] and \
            'Full Body' in dossier['Body']['Morphs++']:
        fbms = dossier['Body']['Morphs++']['Full Body'].keys()
        is_always_thin = 'Thin' in fbms and 'BodyBuilder' not in fbms
        is_never_muscular = 'BodyBuilder' not in fbms

    dynamic_pbms: Iterable[str] = {
        'BicepsFlex', 'FeetForShoe', 'Inhale', 'ToeBigCurl', 'ToeBigSide-Side', 'ToeBigUp-Down',
        'ToesPointed', 'ToesSmallIn', 'ToesSmallUp-Down'}
    if not is_never_muscular:
        dynamic_pbms.update(['CalvesFlex', 'GluteFlexL', 'GluteFlexR'])
    if figure_type == 'Victoria 4':
        dynamic_pbms.update([
            'BreastsDiameter', 'NailsLength', 'NipplesBig', 'NipplesDepth', 'StomachDepth'
        ])
        if not is_always_thin:
            dynamic_pbms.update([
                'BreastDownL', 'BreastDownR', 'BreastInL', 'BreastInR', 'BreastOutL', 'BreastOutR',
                'BreastUpL', 'BreastUpR', 'BreastsCleavage', 'BreastsDroop', 'BreastsFlatten',
                'BreastsHangForward', 'BreastsNatural', 'BreastsPerk',
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

    dynamic_phms: Iterable[str] = {'EyesPupilDialate'}

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

                if phm in dynamic_phms:
                    dynamic_phms.remove(phm)

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

    dynamic_phms = sorted(list(dynamic_phms))
    if len(dynamic_phms) != 0:
        print(f'\n// {figure_type_abbr} Partial Head Morphs++ (dynamic)', file=pz2)
        for phm in dynamic_phms:
            inj_deltas('Morphs++', 'PHM', phm)

    # V4/M4 Control Morphs++
    print(f'\n// {figure_type_abbr} Control Morphs++', file=pz2)
    for ctrl in [
        'ArmsFront-Back', 'ArmsUp-Down', 'EyesSide-Side', 'EyesUp-Down', 'HandGrasp', 'HandSpread',
        'IndexGrasp', 'lArmDown', 'lArmUp', 'MiddleGrasp', 'NeckHeadBend', 'NeckHeadSide-Side',
        'NeckHeadTwist', 'PinkyGrasp', 'rArmDown', 'rArmUp', 'RingGrasp', 'ShoulderShrug', 'ThumbGrasp',
        'TorsoBend', 'TorsoSide-Side', 'TorsoTwist', 'WaistBend']:
        inj_deltas('Morphs++', 'CTRL', ctrl)

    # V4/M4 Elite Morphs
    if 'Body' in dossier and 'Elite' in dossier['Body']:
        print(f'\n// {figure_type_abbr} Elite Morphs', file=pz2)
        for morph_name, morph_values in dossier['Body']['Elite'].items():
            morph_type = 'FBM' if morph_name.endswith('Body') else 'PBM'
            inj_deltas('Elite', morph_type, morph_name)
            morphs['BODY'][morph_type + morph_name] = morph_values

    # V4/M4 Stephanie Morphs
    s4_static_morphs: List[str] = []
    s4_contextual_morphs: List[str] = []
    if figure_type == 'Victoria 4':
        if 'Body' in dossier and 'Stephanie 4' in dossier['Body']:
            for s4_group_name, pbm_group in dossier['Body']['Stephanie 4'].items():
                for morph_name, morph_value in pbm_group.items():
                    if isinstance(morph_value, dict) and 'N' not in morph_value.keys():
                        s4_contextual_morphs.append(morph_name)
                    else:
                        s4_static_morphs.append(morph_name)
                    if s4_group_name == 'Full Body':
                        morphs['BODY']['FBM' + morph_name] = morph_value
                    else:
                        morphs['BODY']['PBM' + morph_name] = morph_value
        if 'PubicDepth' not in s4_static_morphs and 'PubicDepth' not in s4_contextual_morphs:
            s4_contextual_morphs.append('PubicDepth')

        if len(s4_static_morphs) != 0:
            print(f'\n// Stephanie 4 Morphs (static)', file=pz2)
            s4_static_morphs.sort()
            s4_static_morphs.sort(key=lambda morph_name: morph_name.startswith('S4'), reverse=True)
            for morph_name in s4_static_morphs:
                inj_deltas('Stephanie 4', 'PBM' if not morph_name.startswith('S4') else 'FBM',
                           morph_name)

        if len(s4_contextual_morphs) != 0:
            print(f'\n// Stephanie 4 Morphs (contextual)', file=pz2)
            s4_contextual_morphs.sort()
            for morph_name in s4_contextual_morphs:
                inj_deltas('Stephanie 4', 'PBM' if not morph_name.startswith('S4') else 'FBM',
                           morph_name)

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
		{''', file=pz2)
    if not for_ds:
        print('''		groups
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

        if 'MorphTarget' in parm:
            for actor in parm['MorphTarget'].split(','):
                hide_morphs[actor.strip()].append(parm['Name'])

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
		{''', file=pz2)
    if not for_ds and (('Hip' not in dossier or 'Scale' not in dossier['Hip']) or not is_never_muscular or
                       'PubicDepth' in s4_contextual_morphs or
                       ('Muscle' in dossier['Body'] and 'RectusFemorus' in dossier['Body']['Muscle'])):
        print('		groups\n			{', file=pz2)
        if 'Hip' not in dossier or 'Scale' not in dossier['Hip']:
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
        if not is_never_muscular or \
                'PubicDepth' in s4_contextual_morphs or \
                ('Muscle' in dossier['Body'] and 'RectusFemorus' in dossier['Body']['Muscle']):
            print('''			groupNode Morphs | Shapes
				{
				collapsed 0''', file=pz2)
            if not is_never_muscular:
                print('''				groupNode Morphs++
					{
					collapsed 0
					}''', file=pz2)
            if 'PubicDepth' in s4_contextual_morphs:
                print('''				groupNode Stephanie 4
					{
					collapsed 0
					}''', file=pz2)
            if 'Muscle' in dossier['Body'] and 'RectusFemorus' in dossier['Body']['Muscle']:
                print('''				groupNode Muscle
					{
					collapsed 0
					}''', file=pz2)
            print('				}', file=pz2)
        print('			}', file=pz2)

    # write DAZ hip parameters
    for morph_name, morph_values in morphs['hip'].items():
        print(f'		targetGeom {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values)
        print('			}', file=pz2)

    if 'Hip' in dossier:
        if 'yTranslate' in dossier['Hip']:
            print('		translateY ytran\n			{', file=pz2)
            tweak_parm(dossier['Hip']['yTranslate'], TRANSLATION_MULTIPLIER_HIP)
            print('			}', file=pz2)

        if 'Scale' in dossier['Hip']:
            print('		scale scale\n			{', file=pz2)
            tweak_parm(dossier['Hip']['Scale'], SCALE_MULTIPLIER)
            print('			}', file=pz2)

    end_actor()  # hip

    if not for_ds or len(morphs['abdomen']) > 0 or 'Abdomen' in dossier:

        # begin abdomen
        print('''
actor abdomen:1
	{
	channels
		{''', file=pz2)
        if not for_ds:
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
			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}
			}''', file=pz2)

        # write DAZ abdomen parameters
        for morph_name, morph_values in morphs['abdomen'].items():
            print(f'		targetGeom {morph_name}', file=pz2)
            print('			{', file=pz2)
            tweak_parm(morph_values)
            print('			}', file=pz2)

        end_actor()  # abdomen

    if 'Chest' in dossier or len(hide_morphs['chest']) > 0 or len(morphs['chest']) > 0 or \
            (not for_ds and figure_type == 'Victoria 4'):

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

        # hide sub-morphs
        for morph_name in hide_morphs['chest']:
            hide_morph(morph_name)

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

        end_actor()  # chest

    if 'Neck' in dossier or len(hide_morphs['neck']) > 0 or len(morphs['neck']) > 0:

        # begin neck
        print('''
actor neck:1
	{
	channels
		{''', file=pz2)

        # hide sub-morphs
        for morph_name in hide_morphs['neck']:
            hide_morph(morph_name)

        if 'Neck' in dossier and 'yScale' in dossier['Neck']:
            print('		scaleY yScale\n			{', file=pz2)
            tweak_parm(dossier['Neck']['yScale'], SCALE_MULTIPLIER, unhide=True)
            print('			}', file=pz2)

        end_actor()  # neck

    # begin head
    print('''\n\n
actor head:1
	{
	channels
		{''', file=pz2)
    if not for_ds:
        print('''		groups
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

    # hide sub-morphs
    for morph_name in hide_morphs['head']:
        hide_morph(morph_name)

    # write DAZ head parameters
    head = v4_sample.Actor('head')
    for morph_name, morph_values in morphs['head'].items():
        parm = head.Parameter(morph_name)
        print(f'		{"targetGeom" if parm.IsMorphTarget() else "valueParm"} {morph_name}', file=pz2)
        print('			{', file=pz2)
        tweak_parm(morph_values, check_min=parm.MinValue())
        print('			}', file=pz2)

    if 'Scale' in dossier['Head']:
        print('		scale scale\n			{', file=pz2)
        tweak_parm(dossier['Head']['Scale'], SCALE_MULTIPLIER, unhide=True)
        print('			}', file=pz2)

    end_actor()  # head

    # eyes
    if 'Eyes' in dossier or ('Head' in dossier and 'Scale' in dossier['Head']):
        for eye_side in ['r', 'l']:
            print('''\nactor ''' + eye_side + '''Eye:1
	{
	channels
		{''', file=pz2)

            scale = None
            if 'Eyes' in dossier and 'Scale' in dossier['Eyes']:
                scale = dossier['Eyes']['Scale']
            if 'Head' in dossier and 'Scale' in dossier['Head']:
                scale = dossier['Head']['Scale']
            if scale is not None:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, unhide=True)
                print('			}', file=pz2)

            if 'Eyes' in dossier:
                if 'xTranslate' in dossier['Eyes']:
                    print('		translateX xtran\n			{', file=pz2)
                    tweak_parm(dossier['Eyes']['xTranslate'], TRANSLATION_MULTIPLIER_HEAD,
                               unhide=True, negate=eye_side == 'r')
                    print('			}', file=pz2)

                if 'yTranslate' in dossier['Eyes']:
                    print('		translateY ytran\n			{', file=pz2)
                    tweak_parm(dossier['Eyes']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                    print('			}', file=pz2)

                if 'zTranslate' in dossier['Eyes']:
                    print('		translateZ ztran\n			{', file=pz2)
                    tweak_parm(dossier['Eyes']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                    print('			}', file=pz2)

            print('''		}
	}''', file=pz2)

    # upper jaw
    if 'Upper Jaw' in dossier or ('Head' in dossier and 'Scale' in dossier['Head']):
        print('''\nactor upperJaw:1
	{
	channels
		{''', file=pz2)

        scale = None
        if 'Upper Jaw' in dossier and 'Scale' in dossier['Upper Jaw']:
            scale = dossier['Upper Jaw']['Scale']
        if 'Head' in dossier and 'Scale' in dossier['Head']:
            scale = dossier['Head']['Scale']
        if scale is not None:
            print('		scale scale\n			{', file=pz2)
            tweak_parm(scale, SCALE_MULTIPLIER, unhide=True)
            print('			}', file=pz2)

        if 'Upper Jaw' in dossier:
            if 'yTranslate' in dossier['Upper Jaw']:
                print('		translateY ytran\n			{', file=pz2)
                tweak_parm(dossier['Upper Jaw']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                print('			}', file=pz2)

            if 'zTranslate' in dossier['Upper Jaw']:
                print('		translateZ ztran\n			{', file=pz2)
                tweak_parm(dossier['Upper Jaw']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                print('			}', file=pz2)

        print('''		}
	}''', file=pz2)

    # lower jaw
    if 'Lower Jaw' in dossier or ('Head' in dossier and 'Scale' in dossier['Head']):
        print('''\nactor lowerJaw:1
	{
	channels
		{''', file=pz2)

        scale = None
        if 'Lower Jaw' in dossier and 'Scale' in dossier['Lower Jaw']:
            scale = dossier['Lower Jaw']['Scale']
        if 'Head' in dossier and 'Scale' in dossier['Head']:
            scale = dossier['Head']['Scale']
        if scale is not None:
            print('		scale scale\n			{', file=pz2)
            tweak_parm(scale, SCALE_MULTIPLIER, unhide=True)
            print('			}', file=pz2)

        if 'Lower Jaw' in dossier:
            if 'yTranslate' in dossier['Lower Jaw']:
                print('		translateY ytran\n			{', file=pz2)
                tweak_parm(dossier['Lower Jaw']['yTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                print('			}', file=pz2)

            if 'zTranslate' in dossier['Lower Jaw']:
                print('		translateZ ztran\n			{', file=pz2)
                tweak_parm(dossier['Lower Jaw']['zTranslate'], TRANSLATION_MULTIPLIER_HEAD, unhide=True)
                print('			}', file=pz2)

        print('''		}
	}''', file=pz2)

    if 'Tongue' in dossier or ('Head' in dossier and 'Scale' in dossier['Head']):
        print('\n', file=pz2)
        for actor in ['tongueBase', 'tongue01', 'tongue02', 'tongue03', 'tongue04', 'tongue05', 'tongueTip']:
            print('''\nactor ''' + actor + ''':1
	{
	channels
		{''', file=pz2)

            scale = None
            if 'Tongue' in dossier and 'Scale' in dossier['Tongue']:
                scale = dossier['Tongue']['Scale']
            if 'Head' in dossier and 'Scale' in dossier['Head']:
                scale = dossier['Head']['Scale']
            if scale is not None:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, unhide=True)
                print('			}', file=pz2)

            print('''		}
	}''', file=pz2)

    # arms
    for arm_side in ['r', 'l']:
        print('\n', file=pz2)

        # collars
        if len(hide_morphs[arm_side + 'Collar']) > 0 or 'Collars' in dossier:
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

            # hide sub-morphs
            for morph_name in hide_morphs[arm_side + 'Collar']:
                hide_morph(morph_name)

            if 'Collars' in dossier and 'Scale' in dossier['Shoulders']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Collars']['Scale'], SCALE_MULTIPLIER, unhide=True)
                print('			}', file=pz2)

            end_actor()  # collars

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

            end_actor()  # shoulders

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
            if not for_ds and (
                    ('Thighs' not in dossier or 'Scale' not in dossier['Thighs']) or
                    ('Muscle' in dossier['Body'] and 'VastusMedialus' in dossier['Body']['Muscle'])
            ):
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

            end_actor()  # thighs

        if not for_ds or 'Shins' in dossier:
            print('''
actor ''' + leg_side + '''Shin:1
	{
	channels
		{''', file=pz2)

            if not for_ds and \
                    (('Shins' not in dossier or 'Scale' not in dossier['Shins']) or
                     'CalvesFlex' in dynamic_pbms):
                print('''		groups
			{''', file=pz2)
                if 'Shins' not in dossier or 'Scale' not in dossier['Shins']:
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
                if 'CalvesFlex' in dynamic_pbms:
                    print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Shins' in dossier and 'Scale' in dossier['Shins']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Shins']['Scale'], SCALE_MULTIPLIER)
                print('			}', file=pz2)

            end_actor()  # shins

        if not for_ds and 'Feet' in dossier:
            print('''
actor ''' + leg_side + '''Foot:1
	{
	channels
		{''', file=pz2)
            if 'FeetForShoe' in dynamic_pbms:
                print('''		groups
			{''', file=pz2)
                if 'FeetForShoe' in dynamic_pbms:
                    print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            if 'Feet' in dossier and 'Scale' in dossier['Feet']:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(dossier['Feet']['Scale'], SCALE_MULTIPLIER, unhide=True)
                print('			}', file=pz2)

            end_actor()  # feet

        if not for_ds or 'Feet' in dossier or 'Toes' in dossier:
            print('''
actor ''' + leg_side + '''Toe:1
	{
	channels
		{''', file=pz2)

            if not for_ds:
                print('		groups\n			{', file=pz2)
                print('''			groupNode Morphs | Shapes
				{
				collapsed 0
				groupNode Morphs++
					{
					collapsed 0
					}
				}''', file=pz2)
                print('			}', file=pz2)

            scale = None
            if 'Feet' in dossier and 'Scale' in dossier['Feet']:
                scale = dossier['Feet']['Scale']
            if 'Toes' in dossier and 'Scale' in dossier['Toes']:
                scale = dossier['Toes']['Scale']
            if scale is not None:
                print('		scale scale\n			{', file=pz2)
                tweak_parm(scale, SCALE_MULTIPLIER, unhide=True)
                print('			}', file=pz2)

            end_actor()  # toes

    # figure settings
    figure_settings(dossier['Figure'])

    # end writing
    print('}', file=pz2)
    pz2.close()

    # ----------------------------Penis-----------------------------

    if 'Penis' in dossier and figure_type == 'Michael 4':
        penis = dossier['Penis']

        fbms = {}
        if 'Body' in dossier and 'Morphs++' in dossier['Body'] and \
                'Full Body' in dossier['Body']['Morphs++']:
            for fbm_name, fbm_value in dossier['Body']['Morphs++']['Full Body'].items():
                fbms[fbm_name] = fbm_value

        py3_name = character_name.lower() + '_v' + character_version.replace('.', '_') + \
                   '_' + penis['Name'].lower() + '.py'
        py3 = open(os.path.join(py3_dir, py3_name), 'w')
        write_python_script_header(penis['Name'])

        if 'Special' in penis:
            print("\n    body = figure.Actor('BODY')", file=py3)
            for parm in penis['Special'].values():
                if 'MorphTarget' not in parm:
                    print(f"    body.CreateValueParameter('{parm['Name']}')", file=py3)
                else:
                    raise Exception('Penis morphs not supported yet.')

        print('\nelse:', file=py3)

        for actor in ['BODY', 'hip', 'gen01', 'gen04', 'testicles', 'rThigh', 'lThigh']:
            print(f"    {actor} = figure.Actor('{actor}')", file=py3)

            if actor != 'gen04':
                for fbm in ['BodyBuilder', 'Definition', 'Emaciated', 'Jeremy', 'SuperHero', 'Smooth',
                            'Young']:
                    if actor == 'gen01' and fbm != 'Emaciated': continue
                    if actor == 'testicles' and fbm != 'Jeremy': continue
                    if fbm not in fbms:
                        print(f"    {actor}.DeleteTarget('FBM{fbm}')", file=py3)
                if actor == 'BODY':
                    print("    BODY.RemoveValueParameter('Uncircumcised')", file=py3)
                elif actor == 'hip':
                    print("    hip.DeleteTarget('Uncircumcised')", file=py3)
            else:
                for i in range(1, 6):
                    print(f"    gen04.DeleteTarget('PBMUncircumcised0{i}')", file=py3)
            print("", file=py3)

        write_python_script_footer()
        py3.close()

        pz2 = open(os.path.join(
            pz2_dir, f'{character_name} v{character_version} - {penis["Name"]}{"-DS" if for_ds else ""}.pz2'),
            'w', encoding='cp1252', newline='\n')
        write_poser_script_header()
        print('runPythonScript "Runtime:Python:poserScripts:Characters:' + py3_name + '"', file=pz2)

        # begin penis body
        print('''\n\n
actor BODY:1
	{
	channels
		{''', file=pz2)
        if not for_ds:
            print('		groups\n			{', file=pz2)
            print('''			groupNode General
				{
				collapsed 1
				groupNode Transforms
					{
					groupNode Translation
						{
						collapsed 1
						}
					groupNode Rotation
						{
						collapsed 1
						}
					}
				}
			groupNode MorphForms
				{
				collapsed 0
				}''', file=pz2)

            if 'Special' in penis:
                print('			groupNode Special\n				{', file=pz2)
                for parm in penis['Special'].values():
                    print('				parmNode ' + parm['Name'], file=pz2)
                print('				}', file=pz2)

            print('			}', file=pz2)

        if 'Special' in penis:
            for parm in penis['Special'].values():
                special_parm(parm)

        # full-body morphs
        for fbm_name, fbm_value in fbms.items():
            print(f'		targetGeom FBM{fbm_name}', file=pz2)
            print('			{', file=pz2)
            tweak_parm(fbm_value)
            print('			}', file=pz2)

        # partial body morphs
        if 'Body' in dossier:
            for morph_name in ['ScrotumSize']:
                if morph_name in penis['Body']:
                    print(f'		targetGeom PBM{morph_name}', file=pz2)
                    print('			{', file=pz2)
                    tweak_parm(penis['Body'][morph_name])
                    print('			}', file=pz2)

        # penis body scale
        print('		propagatingScale scale\n			{', file=pz2)
        scale = dossier['Body']['Scale']
        if isinstance(scale, dict):
            scale = scale['N']
        tweak_parm(scale, SCALE_MULTIPLIER)
        print('			}', file=pz2)

        end_actor()  # penis body

        # begin penis hip
        print('''\n\n
actor hip:1
	{
	channels
		{''', file=pz2)

        if 'Hip' in penis and 'Scale' in penis['Hip']:
            print('		scale scale\n			{', file=pz2)
            tweak_parm(penis['Hip']['Scale'], SCALE_MULTIPLIER, unhide=True, check_max=2)
            print('			}', file=pz2)

        for xyz in ['x', 'y', 'z']:
            print('		scale' + xyz.upper() + ' ' + xyz + 'Scale\n			{', file=pz2)
            if 'Hip' in penis and (xyz + 'Scale') in penis['Hip']:
                tweak_parm(penis['Hip'][xyz + 'Scale'], SCALE_MULTIPLIER, unhide=True)
            else:
                print('			hidden 0', file=pz2)
            print('			}', file=pz2)

        for xyz in ['x', 'y', 'z']:
            if 'Hip' in penis and (xyz + 'Translate') in penis['Hip']:
                print('		translate' + xyz.upper() + ' ' + xyz + 'tran\n			{', file=pz2)
                tweak_parm(penis['Hip'][xyz + 'Translate'], TRANSLATION_MULTIPLIER_HIP, unhide=True)
                print('			}', file=pz2)

        end_actor()  # penis hip

        # penis abdomen
        if not for_ds:
            print('''
actor abdomen:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				collapsed 1
				}
			}
		}
	}

''', file=pz2)

        for actor in ['gen01', 'gen02', 'gen03', 'gen04', 'testicles']:
            print('''
actor ''' + actor + ''':1
	{
	channels
		{''', file=pz2)
            if not for_ds and actor in ['gen01', 'gen04', 'testicles']:
                print('''		groups
			{
			groupNode Morphs | Shapes
				{
				collapsed 1
				}
			}''', file=pz2)

            if actor in penis:
                if 'Scale' in penis[actor]:
                    print('		scale scale\n			{', file=pz2)
                    tweak_parm(penis[actor]['Scale'], SCALE_MULTIPLIER)
                    print('			}', file=pz2)

                for xyz in ['x', 'y', 'z']:
                    if actor in penis and (xyz + 'Scale') in penis[actor]:
                        print('		scale' + xyz.upper() + ' ' + xyz + 'Scale\n			{', file=pz2)
                        tweak_parm(penis[actor][xyz + 'Scale'], SCALE_MULTIPLIER)
                        print('			}', file=pz2)

                if 'Bend' in penis[actor]:
                    print('		rotateX xrot\n			{', file=pz2)
                    tweak_parm(penis[actor]['Bend'])
                    print('			}', file=pz2)

            end_actor()

        # penis thighs
        if not for_ds:
            print('\n', file=pz2)
            for leg_side in ['r', 'l']:
                print('''
actor ''' + leg_side + '''Thigh:1
	{
	channels
		{
		groups
			{
			groupNode General
				{
				collapsed 1
				}
			groupNode Morphs | Shapes
				{
				collapsed 1
				}
			}
		}
	}''', file=pz2)

        figure_settings(penis)
        print('}', file=pz2)
        pz2.close()


def write_python_script_header(character_name: str) -> None:
    global py3
    print(f"""import poser

# this script is executed twice
figure = poser.Scene().CurrentFigure()
if figure.Name() != '{character_name.upper()}':
    figure.SetName('{character_name.upper()}')""", file=py3)


def write_python_script_footer() -> None:
    global py3
    print("""    poser.ExecFile('../MAHDI/figure_remove_empty_daz_params_silent.py')
    poser.ExecFile('../MAHDI/character_material_loader.py')""", file=py3)


def write_poser_script_header() -> None:
    global pz2
    print('{\n\nversion\n	{\n	number ' + str(POSER_VERSION) + '\n	}\n', file=pz2)


def morph_target_path(character_name: str, morph_name: str, ext: str) -> str:
    global figure_type_abbr
    return os.path.join(
        os.environ['ONEDRIVE'], 'Projects', 'Characters', character_name,
        'Sculpture on ' + figure_type_abbr, morph_name + '.' + ext)


def inj_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:InjDeltas.{type}{name}.pz2"',
          file=pz2)


def rem_deltas(group: str, type: str, name: str) -> str:
    global pz2, figure_type
    print(f'readScript "Runtime:Libraries:!DAZ:{figure_type}:Deltas:{group}:RemDeltas.{type}{name}.pz2"',
          file=pz2)


def special_parm(parm: Dict[str, Any]) -> None:
    global pz2

    parm_type = 'valueParm'
    if 'MorphTarget' in parm:
        parm_type = 'targetGeom'

    init_value = '0'
    if 'Default' in parm:
        init_value = parm['Default']
    elif 'MorphTarget' in parm:
        init_value = '1'

    min_val, max_val = '0', '1'
    if 'Min' in parm:
        min_val = parm['Min']
    if 'Max' in parm:
        max_val = parm['Max']

    sensitivity = '0.004'
    if 'Sensitivity' in parm:
        sensitivity = parm['Sensitivity']
    elif 'MorphTarget' in parm:
        sensitivity = '1'

    master_synched = '0'
    if 'MasterSynched' in parm:
        master_synched = '1'

    print('''		''' + parm_type + ''' ''' + parm['Name'] + '''
			{
			initValue ''' + init_value + '''
			min ''' + min_val + '''
			max ''' + max_val + '''
			trackingScale ''' + sensitivity + '''
			masterSynched ''' + master_synched + '''
			keys
				{
				k  0  ''' + init_value + '''
				}''', file=pz2)

    if 'Dependencies' in parm:
        value_ops: Dict[str, str] = {}
        for dep_abbr, dep_value in parm['Dependencies'].items():
            specials = dossier['Body']['Special']
            if penis is not None: specials = penis['Special']
            value_ops[specials[dep_abbr]['Name']] = dep_value
        value_op_delta_add(value_ops, 1, False)

    print('			}', file=pz2)


def tweak_parm(
        user_entry: Any,
        multiplier: float = 1,
        negate: bool = False,
        unhide: bool = False,
        check_min: Optional[float] = None,
        check_max: Optional[float] = None,
) -> None:
    global dossier, pz2

    value = None
    value_ops = {}
    if isinstance(user_entry, dict):
        for k, v in user_entry.items():
            if k == 'N':
                value = user_entry['N']
            elif penis is None:
                value_ops[dossier['Body']['Special'][k]['Name']] = v
            else:
                value_ops[penis['Special'][k]['Name']] = v
    else:
        value = user_entry

    if value is not None:
        fl = float(value.strip()) * multiplier
        if negate: fl = -fl
        print('			initValue ' + poser_float(fl), file=pz2)
    if unhide: print('			hidden 0', file=pz2)
    if value is not None:
        if check_min is not None and fl < check_min:
            print('			min ' + poser_float(fl), file=pz2)
        if check_max is not None and fl > check_max:
            print('			max ' + poser_float(fl), file=pz2)
        print('''			keys
				{
				k  0  ''' + poser_float(fl) + '''
				}''', file=pz2)
    if len(value_ops) != 0:
        value_op_delta_add(value_ops, multiplier, negate)


def poser_float(fl: float) -> str:
    if fl % 1 == 0:
        return str(fl).split('.')[0]
    else:
        for decimals in range(4, 8):
            rounded = round(fl, decimals)
            if abs(fl - rounded) < 1e-10:  # 0.00000001
                fl = rounded
                break
        return str(fl).rstrip('0').rstrip('.')


def value_op_delta_add(
        value_ops: Dict[str, str],
        multiplier: float,
        negate: bool,
) -> None:
    for parm_name, parm_value in value_ops.items():
        print(f'''			valueOpDeltaAdd
				Figure 1
				BODY:1
				{parm_name}
				deltaAddDelta {value_op_number(parm_value, multiplier, negate)}''', file=pz2)


def value_op_number(s: str, multiplier: float, negate: bool) -> str:
    ss = s.strip()
    fl = float((ss[-1] if ss[-1] == '-' else '') + ss[1:-2]) * multiplier
    if negate: fl = -fl
    return poser_float(fl)


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


def hide_morph(morph_name: str) -> None:
    global pz2
    print('''		targetGeom ''' + morph_name + '''
			{
			hidden 1
			}''', file=pz2)


def end_actor():
    global pz2
    print('		}\n	}', file=pz2)


def figure_settings(settings: Dict[str, Any]):
    global pz2

    print('''\n\n
figure
	{''', file=pz2)

    if 'Subdivision' in settings:
        print('	subdivLevels 0', file=pz2)
        print('	subdivRenderLevels ' + settings['Subdivision'], file=pz2)

    # skinning method
    print('	skinType 3', file=pz2)  # Poser Unimesh

    print('	}', file=pz2)


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
