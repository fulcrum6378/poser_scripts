import os
import poser
import shutil

import fantasy_render_preconditions
from doc_collect_required_content import collect_pz3_required_paths, copy_to

SCENES = '\\\\NERA\\Scenes\\'
CONTENT = '\\\\NERA\\Content\\'

scene = poser.Scene()
doc_path = scene.DocumentPath()

errors = fantasy_render_preconditions.check_scene()
continuum = len(errors) == 0
if not continuum:
    continuum = poser.DialogSimple.YesNo(errors + 'Do you want to continue?') == 1

if continuum and scene.Changed() == 1 and not poser.DialogSimple.YesNo('Unsaved document. Continue?'):
    continuum = False

pz3: str
if continuum:
    def replace_parameter(parm_name: str, parm_value: str) -> None:
        global pz3, cur
        full_parm = f'	{parm_name} '
        cur = pz3.index(full_parm, cur) + len(full_parm)
        pz3 = pz3[:cur] + parm_value + pz3[pz3.index('\n', cur):]


    def delete_actor(actor_name) -> None:
        global pz3, cur
        act_beg = pz3.index('\ncontrolProp ' + actor_name + '\n', cur)
        cur = act_beg
        act_end = pz3.index('\n	}\n', cur) + 3  # not 4
        pz3 = pz3[:act_beg] + pz3[act_end:]


    def consume_material_actor(actor_name: str, shader_root_name: str) -> str:
        global pz3, cur
        act_beg = pz3.index('\ncontrolProp ' + actor_name + '\n', cur)
        cur = act_beg
        shd_beg = pz3.index('\n		shaderTree\n', cur) + 14
        cur = shd_beg
        shd_end = pz3.index('superflyRoot "' + shader_root_name + '" \n			}\n', cur) + \
                  (22 + len(shader_root_name))
        shader_tree = pz3[shd_beg:shd_end]
        act_end = pz3.index('\n	}\n\n', cur) + 4  # not 5
        pz3 = pz3[:act_beg] + pz3[act_end:]
        cur = act_beg - 10
        return shader_tree


    pz3 = open(doc_path, 'r', encoding='cp1252').read()
    cur = 0

    # delete unnecessary actors
    delete_actor('BackgroundMaterialActor')
    delete_actor('AtmosphereMaterialActor')

    # cut shader trees from BackgroundMaterialActor and AtmosphereMaterialActor
    bg_shader_tree = '	bgShaderTree\n' + consume_material_actor(
        'BackgroundMaterialActor', 'Background'
    )
    atmos_shader_tree = '	atmosShaderTree\n' + consume_material_actor(
        'AtmosphereMaterialActor', 'Atmosphere'
    )

    # modernise the background shader tree
    bg_shader_tree = bg_shader_tree.replace(  # Mapping:Vector Type => Texture
        'name "Vector Type"\n					value 4 0 0',
        'name "Vector Type"\n					value 3 0 0',
    )

    cur = pz3.rindex('\n\ndoc\n	{\n')

    # lower preview graphics to prevent out of memory errors
    replace_parameter('displayMode', 'EDGESONLY')

    # delete unnecessary actors
    cur = pz3.index('	addActor BackgroundMaterialActor', cur)
    pz3 = pz3[:cur] + pz3[cur + 34:]
    cur = pz3.index('	addActor AtmosphereMaterialActor', cur)
    pz3 = pz3[:cur] + pz3[cur + 34:]

    cur = pz3.index('\n\nrenderDefaults \n	{\n', cur)

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

    # paste bgShaderTree and atmosShaderTree
    cur = pz3.rindex('\n	superFlyOptions\n		{\n', cur)
    pz3 = pz3[:cur] + bg_shader_tree + pz3[cur:]
    cur += len(bg_shader_tree)
    pz3 = pz3[:cur] + atmos_shader_tree + pz3[cur:]

    # disable Branched Path Tracing
    # noinspection PyRedeclaration
    cur = pz3.rindex('\n	superFlyOptions\n		{\n') + 22
    # pz3 = pz3[:cur] + '		aaSamples 22\n' + pz3[cur:]
    pz3 = pz3[:cur] + '		advancedSamplingControls 0\n' + pz3[cur:]

    # check if the destination directory exists
    nera_offline = False
    if not os.path.isdir(SCENES):
        if poser.DialogSimple.YesNo('Nera is unavailable. Save in Desktop?') == 1:
            SCENES = os.environ['USERPROFILE'] + '\\Desktop\\'
            nera_offline = True
        else:
            continuum = False

    # check if the file doesn't already exist
    if continuum:
        SCENES += os.path.basename(doc_path)
        if os.path.isfile(SCENES):
            continuum = poser.DialogSimple.YesNo('The scene is already queued. Overwrite?')

    # write the files
    if continuum:
        open(SCENES, 'w', encoding='cp1252').write(pz3)
        pmd_path = doc_path.replace('.pz3', '.pmd')
        if os.path.isfile(pmd_path):
            shutil.copy2(pmd_path, SCENES.replace('.pz3', '.pmd'))

        # write required content
        if not nera_offline:
            copy_to(CONTENT, collect_pz3_required_paths(doc_path)[0])

        poser.DialogSimple.MessageBox('Ready to render in Poser 11...')
