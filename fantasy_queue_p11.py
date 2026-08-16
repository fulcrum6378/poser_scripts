import os
import shutil

import poser

from collect_required_content import collect_pz3_required_paths, copy_to
from fantasy_extract_poses_pz3 import CHARACTERS

scene = poser.Scene()
errors = ''
for figure in scene.Figures():
    if figure.Name() not in CHARACTERS: continue
    for material in figure.Materials():
        for node in material.ShaderTree().Nodes():
            if node.Type() == 'CyclesSurface' and \
                    material.ShaderTree().RendererRootNode(poser.kRenderEngineCodeSUPERFLY).Name() != node.Name():
                errors += f'CyclesSurface in {figure.Name().capitalize()}\'s {material.Name()} is disabled!\n'

continuum = len(errors) == 0
if not continuum:
    continuum = poser.DialogSimple.YesNo(errors + 'Do you want to continue?') == 1

if continuum and scene.Changed() == 1 and not poser.DialogSimple.YesNo('Unsaved document. Continue?'):
    continuum = False

if continuum:
    errors = ''
    for light in scene.Lights():
        if light.LightType() == 3 and light.LightOn() == 0:
            errors += f'{light.Name()} is off!\n'
    continuum = len(errors) == 0 or poser.DialogSimple.YesNo(errors + 'Do you want to continue?') == 1

pz3: str
if continuum:
    def replace_parameter(parm_name: str, parm_value: str):
        global pz3, cur
        full_parm = f'	{parm_name} '
        cur = pz3.find(full_parm, cur) + len(full_parm)
        pz3 = pz3[:cur] + parm_value + pz3[pz3.find('\n', cur):]


    pz3_path = scene.DocumentPath()
    pz3 = open(pz3_path, 'r', encoding='cp1252').read()

    # lower preview graphics to prevent memory leakage
    cur = pz3.rfind('\n\ndoc\n	{\n')
    replace_parameter('displayMode', 'EDGESONLY')

    cur = pz3.find('\n\nrenderDefaults \n	{\n', cur)

    # prepare for a big render (not part of downgrading!)
    # replace_parameter('newWinWidth', '2560')
    # replace_parameter('newWinHeight', '1920')

    # lower preview graphics to prevent memory leakage
    replace_parameter('hardwareShading', '0')
    replace_parameter('previewAASamples', '1')
    replace_parameter('previewMipMaps', '0')
    replace_parameter('previewTransLimit', '0.5')
    replace_parameter('doPreviewMultisample', '0')
    replace_parameter('realtimeShowBackfaces', '1')

    # disable Branched Path Tracing
    # noinspection PyRedeclaration
    cur = pz3.rfind('\n	superFlyOptions\n		{\n') + 22
    # pz3 = pz3[:cur] + '		aaSamples 22\n' + pz3[cur:]
    pz3 = pz3[:cur] + '		advancedSamplingControls 0\n' + pz3[cur:]

    # check if the destination directory exists
    destination = '\\\\NERA\\Scenes\\'
    if not os.path.isdir(destination):
        if poser.DialogSimple.YesNo('Nera is unavailable. Save in Desktop?') == 1:
            destination = os.environ['USERPROFILE'] + '\\Desktop\\'
        else:
            continuum = False

    # check if the file doesn't already exist
    if continuum:
        destination += os.path.basename(pz3_path)
        if os.path.isfile(destination):
            continuum = poser.DialogSimple.YesNo('The scene is already queued. Overwrite?')

    # write the files
    if continuum:
        open(destination, 'w', encoding='cp1252').write(pz3)
        pmd_path = pz3_path.replace('.pz3', '.pmd')
        if os.path.isfile(pmd_path):
            shutil.copy2(pmd_path, destination.replace('.pz3', '.pmd'))

        # write required content
        copy_to('\\\\NERA\\Content\\', collect_pz3_required_paths(scene.DocumentPath())[0])

        poser.DialogSimple.MessageBox('Ready to render in Poser 11...')
