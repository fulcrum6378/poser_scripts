import os
import poser
from typing import Any, Dict, Optional, Tuple

import quick_yaml


def convenience_material_name(mat_name):
    return {
        'EyeSocket': '1_EyeSocket',
        'Eyebrow': '1_Eyebrow',
        'EyeBrow': '1_Eyebrow',
        'Lip': '1_Lip',
        'Nostril': '1_Nostril',
        'SkinFace': '1_SkinFace',
        'Nipple': '2_Nipple',
        'SkinHead': '2_SkinHead',
        'SkinNeck': '2_SkinNeck',
        'SkinTorso': '2_SkinTorso',
        'SkinHip': '2_SkinHip',
        'Fingernail': '3_Fingernail',
        'FingerNail': '3_Fingernail',
        'SkinArm': '3_SkinArm',
        'SkinFoot': '3_SkinFoot',
        'SkinForearm': '3_SkinForearm',
        'SkinHand': '3_SkinHand',
        'SkinLeg': '3_SkinLeg',
        'Toenail': '3_Toenail',
        'ToeNail': '3_Toenail',
        'InnerMouth': '4_InnerMouth',
        'Gums': '4_Gums',
        'Teeth': '4_Teeth',
        'Tongue': '4_Tongue',
        'Cornea': '5_Cornea',
        'Iris': '5_Iris',
        'Lacrimal': '5_Lacrimal',
        'Lacrimals': '5_Lacrimal',
        'Pupil': '5_Pupil',
        'Pupils': '5_Pupil',
        'Sclera': '5_Sclera',
        'Eyelash': '6_Eyelash',
        'Eyelashes': '6_Eyelash',
        'EyeSurface': '7_EyeSurface',
        'Tear': '7_Tear',
    }[mat_name]


def convenience_color(any_str: str) -> Tuple[float, float, float]:
    try:
        return float(any_str) / 255.0, float(any_str) / 255.0, float(any_str) / 255.0
    except ValueError:
        pass
    if ', ' in any_str:
        spl = any_str.split(', ')
        return float(spl[0]) / 255.0, float(spl[1]) / 255.0, float(spl[2]) / 255.0
    if any_str.startswith('#') or any_str.startswith('0x'):
        any_str = any_str.replace('#', '').replace('0x', '')
        return int(any_str[0:2], 16) / 255.0, int(any_str[2:4], 16) / 255.0, int(any_str[4:6], 16) / 255.0
    return 0, 0, 0


scene = poser.Scene()
figure = scene.CurrentFigure()
character = figure.Name().capitalize()
dossier_dir = os.environ['ONEDRIVE'] + rf'\Projects\Characters\{character}\Dossier'
if not os.path.isdir(dossier_dir):
    raise Exception('This character has no dossier directory.')
manifest_path: Optional[str] = None
for dossier_file in os.listdir(dossier_dir).__reversed__():
    if dossier_file.endswith('.yml'):
        manifest_path = os.path.join(dossier_dir, dossier_file)
        break
# noinspection PyTypeChecker
manifest = quick_yaml.load(open(manifest_path, 'r').read())

for mat in figure.Materials():
    mat_name = mat.Name()
    # if mat_name not in ['2_SkinTorso']:
    #    continue  # TODO REMOVE

    tree = mat.ShaderTree()
    previous_nodes = tree.Nodes()
    phs = tree.CreateNode('PhysicalSurface')
    for previous_node in previous_nodes:
        tree.DeleteNode(previous_node)

    node_row_1, node_row_2, node_row_3 = 20, 245, 470
    node_column_1, node_column_2, node_column_3 = 20, 20, 20

    phs.SetName('PhysicalSurface')
    phs.SetLocation(node_row_1, node_column_1)
    tree.SetRendererRootNode(poser.kRenderEngineCodeFIREFLY, phs)
    if mat_name == '1_Eyebrow':  # in ['1_Eyebrow', '5_Cornea']:
        phs.SetInputsCollapsed(True)
        phs.SetPreviewVisible(True)
    node_column_1 += 90

    # ------------------------Parse-Manifest--------------------------

    shader: Optional[Dict[str, Any]] = None
    try:
        shader = manifest['Shaders'][{
            '1_EyeSocket': 'Face',
            '1_Lip': 'Lips',
            '1_Nostril': 'Face',
            '1_SkinFace': 'Face',
            '2_Nipple': 'Torso',
            '2_SkinHead': 'Torso',
            '2_SkinNeck': 'Torso',
            '2_SkinTorso': 'Torso',
            '2_SkinHip': 'Torso',
            '3_Fingernail': 'Limbs',
            '3_SkinArm': 'Limbs',
            '3_SkinFoot': 'Limbs',
            '3_SkinForearm': 'Limbs',
            '3_SkinHand': 'Limbs',
            '3_SkinLeg': 'Limbs',
            '3_Toenail': 'Limbs',
            '4_InnerMouth': 'Mouth',
            '4_Gums': 'Mouth',
            '4_Teeth': 'Mouth',
            '4_Tongue': 'Mouth',
            '5_Iris': 'Eyes',
            '5_Lacrimal': 'Lacrimal',
            '5_Sclera': 'Eyes',
            '6_Eyelash': 'Eyelashes',
        }[mat_name]]
    except KeyError:
        pass

    if mat_name == '5_Lacrimal' and 'Eyes' in manifest['Shaders']:
        # shader |= manifest['Shaders']['Eyes']  # Python 3.9
        shader = {**shader, **manifest['Shaders']['Eyes']}

    diffuse_texture: Optional[str] = None
    color_math = None
    diffuse_hue, diffuse_saturation, diffuse_brightness = None, None, None
    hsv: Optional[Tuple] = None
    if shader is not None and 'DiffuseTextures' in shader:
        diffuse_texture = shader['DiffuseTextures'] \
            [0 if len(shader['DiffuseTextures']) == 1 or 'DiffuseTextureDefault' not in shader \
                else (int(shader['DiffuseTextureDefault']) - 1)]
        if 'DiffuseHue' in shader:
            diffuse_hue = shader['DiffuseHue']
        if 'DiffuseSaturation' in shader:
            diffuse_saturation = shader['DiffuseSaturation']
        if 'DiffuseBrightness' in shader:
            diffuse_brightness = shader['DiffuseBrightness']
    if diffuse_hue is not None or diffuse_saturation is not None or diffuse_brightness is not None:
        hsv = (diffuse_hue if diffuse_hue is not None else 0,
               diffuse_saturation if diffuse_saturation is not None else 1,
               diffuse_brightness if diffuse_brightness is not None else 1)

    opacity_texture: Optional[str] = None
    if shader is not None and 'OpacityTextures' in shader:
        opacity_texture = shader['OpacityTextures'] \
            [0 if len(shader['OpacityTextures']) == 1 or 'OpacityTextureDefault' not in shader \
                else (int(shader['OpacityTextureDefault']) - 1)]

    # -----------------------PhysicalSurface--------------------------

    # PhysicalSurface : Color
    if mat_name in ['1_Eyebrow', '5_Cornea', '5_Pupil', 'Preview']:
        color = (0, 0, 0)
    else:
        color = (1, 1, 1)
        if shader is not None and 'Color' in shader:
            if isinstance(shader['Color'], dict):
                for easy_name, easy_color in shader['Color'].items():
                    if easy_name.lower() == 'all' or convenience_material_name(easy_name) == mat_name:
                        color = convenience_color(easy_color)
            else:
                color = convenience_color(shader['Color'])
    phs.InputByInternalName('Color').SetColor(color[0], color[1], color[2])

    # PhysicalSurface : Transparency
    trans = 0
    if mat_name in ['5_Cornea', '7_EyeSurface', '7_Tear', 'Preview'] or opacity_texture is not None:
        trans = 1
    phs.InputByInternalName('Transparency').SetFloat(trans)

    # PhysicalSurface : Roughness
    rough = 0
    if shader is not None and 'Roughness' in shader:
        if isinstance(shader['Roughness'], dict):
            for easy_name, value in shader['Roughness'].items():
                if easy_name.lower() == 'all' or convenience_material_name(easy_name) == mat_name:
                    rough = float(value)
        else:
            rough = float(shader['Roughness'])
    phs.InputByInternalName('Roughness').SetFloat(rough)

    # PhysicalSurface : Specular
    if mat_name in ['7_EyeSurface']:
        spec = (0.5, 0.5, 0.5)
    elif mat_name in ['7_Tear']:
        spec = (1, 1, 1)
    else:
        spec = (0, 0, 0)
        if shader is not None and 'Specular' in shader:
            if isinstance(shader['Specular'], dict):
                for easy_name, easy_color in shader['Specular'].items():
                    if easy_name.lower() == 'all' or convenience_material_name(easy_name) == mat_name:
                        spec = convenience_color(easy_color)
            else:
                spec = convenience_color(shader['Specular'])
    phs.InputByInternalName('Specular').SetColor(spec[0], spec[1], spec[2])

    # PhysicalSurface : Metallic
    if mat_name in ['7_EyeSurface', '7_Tear']:
        phs_metal = phs.InputByInternalName('Metallic')
        if mat_name == '7_EyeSurface':
            phs_metal.SetFloat(0.04)
        elif mat_name == '7_Tear':
            phs_metal.SetFloat(0.1)

    # PhysicalSurface : Emission
    phs.InputByInternalName('Emission').SetColor(0, 0, 0)

    # PhysicalSurface : SSS
    phs_sss_group = phs.InputByInternalName('Scatter_Group')
    if mat_name in ['3_Fingernail', '3_Toenail']:
        phs_sss_group.SetFloat(2)
    elif mat_name in ['5_Cornea', '5_Sclera']:
        phs_sss_group.SetFloat(3)
    elif mat_name in ['4_Gums', '4_InnerMouth', '4_Teeth', '4_Tongue']:
        phs_sss_group.SetFloat(4)
    phs.InputByInternalName('SSSMethod').SetFloat(1)

    # -------------------------Dependencies---------------------------

    if diffuse_texture is not None:
        dif_map = tree.CreateNode('image_map')
        dif_map.SetName('ColorTexture')
        dif_map.SetLocation(node_row_2, node_column_2)
        dif_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + diffuse_texture)
        dif_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Color'))
        dif_map.SetInputsCollapsed(True)
        dif_map.SetPreviewVisible(True)
        node_column_2 += 255

    if opacity_texture is not None:
        opa_map = tree.CreateNode('image_map')
        opa_map.SetName('OpacityTexture')
        opa_map.SetLocation(node_row_2, node_column_2)
        opa_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + opacity_texture)
        opa_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Transparency'))
        if spec != (0, 0, 0):
            opa_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Specular'))
        opa_map.SetInputsCollapsed(True)
        opa_map.SetPreviewVisible(True)
        node_column_2 += 255

    # -------------------------Cycles-Shaders-------------------------

    if mat_name in ['7_Tear', '7_EyeSurface']:
        phs.SetInputsCollapsed(True)
        cyc = tree.CreateNode('CyclesSurface')
        cyc.SetLocation(node_row_1, node_column_1)
        tree.SetRendererRootNode(poser.kRenderEngineCodeSUPERFLY, cyc)
        node_column_1 += 130

        if mat_name == '7_EyeSurface':
            clo1 = tree.CreateNode('ccl_MixClosure')
            clo1.SetLocation(node_row_1, node_column_1)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            math = tree.CreateNode('ccl_Math')
            math.SetLocation(node_row_2, node_column_2)
            math.InputByInternalName('Type').SetFloat(1)
            math.OutputByInternalName('Value').ConnectToInput(clo1.InputByInternalName('Closure1'))
            node_column_2 += 145

            light_path = tree.CreateNode('ccl_LightPath')
            light_path.SetLocation(node_row_3, node_column_3)
            light_path.OutputByInternalName('Is Shadow Ray').ConnectToInput(math.InputByInternalName('Value1'))
            light_path.OutputByInternalName('Is Diffuse Ray').ConnectToInput(math.InputByInternalName('Value2'))

            glass_bsdf = tree.CreateNode('ccl_GlassBsdf')
            glass_bsdf.SetLocation(node_row_2, node_column_2)
            glass_bsdf.InputByInternalName('Color').SetColor(1, 1, 1)
            glass_bsdf.InputByInternalName('Roughness').SetFloat(0.02)
            glass_bsdf.InputByInternalName('IOR').SetFloat(1.376)
            glass_bsdf.InputByInternalName('Distribution').SetFloat(2)
            glass_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
            node_column_2 += 145

            transparent_bsdf = tree.CreateNode('ccl_TransparentBsdf')
            transparent_bsdf.SetLocation(node_row_2, node_column_2)
            transparent_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))


        elif mat_name == '7_Tear':
            clo1 = tree.CreateNode('ccl_AddClosure')
            clo1.SetLocation(node_row_1, node_column_1)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            node_column_2 = 232
            transparent_bsdf = tree.CreateNode('ccl_TransparentBsdf')
            transparent_bsdf.SetLocation(node_row_2, node_column_2)
            transparent_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
            node_column_2 += 74

            refraction_bsdf = tree.CreateNode('ccl_RefractionBsdf')
            refraction_bsdf.SetLocation(node_row_2, node_column_2)
            refraction_bsdf.InputByInternalName('Color').SetColor(0.3, 0.3, 0.3)
            refraction_bsdf.InputByInternalName('IOR').SetFloat(1.33)
            refraction_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))

    # print(dir(root))
    # for inp in root.Inputs():
    #    print(inp.InternalName())
    # tree = poser.Scene().CurrentFigure().Material('7_Tear').ShaderTree()

# - every node is 105 px wide.
# - CyclesSurface is 117 px tall.
