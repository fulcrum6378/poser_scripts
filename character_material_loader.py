import os
import poser
from typing import Any, Dict, Optional, Tuple

import quick_yaml


def convenience_is_same_material(easy_name: str, mat_name: str) -> bool:
    if easy_name.lower() == mat_name.lower(): return True
    if easy_name.lower() == mat_name[2:].lower(): return True
    if easy_name.lower() + 's' == mat_name[2:].lower(): return True
    if (easy_name.lower() == 'nail' or easy_name.lower() == 'nails') and \
            (mat_name == '3_Fingernail' or mat_name == '3_Toenail'): return True
    return False


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


def get_value_for_this_mat(user_input: Any, default: Any) -> Any:  # float | str
    global chosen_mode
    if isinstance(user_input, dict):
        for easy_name, value in user_input.items():
            if easy_name.lower() == 'all' or convenience_is_same_material(easy_name, mat_name):
                if isinstance(value, list):
                    return value[chosen_mode]
                else:
                    return value
            break
        return default
    elif isinstance(user_input, list):
        return user_input[chosen_mode]
    else:
        return user_input


def get_color_for_this_mat(user_input: Any, default: \
        Tuple[float, float, float]) -> \
        Tuple[float, float, float]:
    global chosen_mode
    if isinstance(user_input, dict):
        for easy_name, easy_color in user_input.items():
            if easy_name.lower() == 'all' or convenience_is_same_material(easy_name, mat_name):
                if isinstance(easy_color, list):
                    return convenience_color(easy_color[chosen_mode])
                else:
                    return convenience_color(easy_color)
            break
        return default
    elif isinstance(user_input, list):
        return convenience_color(user_input[chosen_mode])
    else:
        return convenience_color(user_input)


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
    tree = mat.ShaderTree()
    previous_nodes = tree.Nodes()
    phs = tree.CreateNode('PhysicalSurface')
    for previous_node in previous_nodes:
        tree.DeleteNode(previous_node)

    node_column_1_x, node_column_2_x, node_column_3_x = 20, 245, 470
    node_column_1_y, node_column_2_y, node_column_3_y = 20, 20, 20

    phs.SetName('PhysicalSurface')
    phs.SetLocation(node_column_1_x, node_column_1_y)
    tree.SetRendererRootNode(poser.kRenderEngineCodeFIREFLY, phs)
    if mat_name in ['1_Eyebrow', 'Preview']:  # '5_Cornea'
        phs.SetInputsCollapsed(True)
        phs.SetPreviewVisible(True)
    node_column_1_y += 90

    # ------------------------Parse-Manifest--------------------------

    shader: Dict[str, Any] = {}
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

    # merge the `Eyes` shader into `Lacrimal`
    if mat_name == '5_Lacrimal' and 'Eyes' in manifest['Shaders']:
        # shader |= manifest['Shaders']['Eyes']  # Python 3.9
        shader = {**shader, **manifest['Shaders']['Eyes']}

    chosen_mode = 0
    if 'DefaultMode' in shader:
        chosen_mode = int(shader['DefaultMode']) - 1

    diffuse_texture: Optional[str] = None
    diffuse_math = None
    diffuse_hue, diffuse_saturation, diffuse_brightness = None, None, None
    diffuse_hsv: Optional[Tuple] = None
    if 'ColorTexture' in shader:
        diffuse_texture = get_value_for_this_mat(shader['ColorTexture'], None)
        if diffuse_texture == 'null': diffuse_texture = None
        if 'DiffuseHue' in shader:
            diffuse_hue = get_value_for_this_mat(shader['DiffuseHue'], None)
        if 'DiffuseSaturation' in shader:
            diffuse_saturation = get_value_for_this_mat(shader['DiffuseSaturation'], None)
        if 'DiffuseBrightness' in shader:
            diffuse_brightness = get_value_for_this_mat(shader['DiffuseBrightness'], None)
        if diffuse_hue is not None or diffuse_saturation is not None or diffuse_brightness is not None:
            # noinspection PyTypeChecker
            diffuse_hsv = (float(diffuse_hue) if diffuse_hue is not None else 0,
                           float(diffuse_saturation) if diffuse_saturation is not None else 1,
                           float(diffuse_brightness) if diffuse_brightness is not None else 1)

    opacity_texture: Optional[str] = None
    if 'OpacityTexture' in shader:
        opacity_texture = get_value_for_this_mat(shader['OpacityTexture'], None)

    bump_texture: Optional[str] = None
    if 'BumpTexture' in shader:
        bump_texture = get_value_for_this_mat(shader['BumpTexture'], None)

    # -----------------------PhysicalSurface--------------------------

    # PhysicalSurface : Color
    color = (1, 1, 1)
    if mat_name in ['1_Eyebrow', '5_Cornea', '5_Pupil', 'Preview']:
        color = (0, 0, 0)
    elif 'Color' in shader:
        color = get_color_for_this_mat(shader['Color'], color)
    phs.InputByInternalName('Color').SetColor(color[0], color[1], color[2])

    # PhysicalSurface : Transparency
    trans = 0
    if mat_name in ['5_Cornea', '7_EyeSurface', '7_Tear', 'Preview'] or opacity_texture is not None:
        trans = 1
    phs.InputByInternalName('Transparency').SetFloat(trans)
    if opacity_texture is not None:
        phs.InputByInternalName('TransparencyMode').SetFloat(1)

    # PhysicalSurface : Roughness
    rough = 0
    if 'Roughness' in shader:
        rough = float(get_value_for_this_mat(shader['Roughness'], rough))
    phs.InputByInternalName('Roughness').SetFloat(rough)

    # PhysicalSurface : Specular
    spec = (0, 0, 0)
    if mat_name == '7_EyeSurface':
        spec = (0.5, 0.5, 0.5)
    elif mat_name == '7_Tear':
        spec = (1, 1, 1)
    elif 'Specular' in shader:
        spec = get_color_for_this_mat(shader['Specular'], spec)
    phs.InputByInternalName('Specular').SetColor(spec[0], spec[1], spec[2])

    # PhysicalSurface : Metallic
    if mat_name in ['7_EyeSurface', '7_Tear']:
        metal = 0
        if mat_name == '7_EyeSurface':
            metal = 0.04
        elif mat_name == '7_Tear':
            metal = 0.1
        phs.InputByInternalName('Metallic').SetFloat(metal)

    # PhysicalSurface : Emission
    phs.InputByInternalName('Emission').SetColor(0, 0, 0)

    # PhysicalSurface : Bump
    bump = 0
    if 'Bump' in shader:
        bump = float(get_value_for_this_mat(shader['Bump'], bump)) * 0.3937
    phs.InputByInternalName('Bump').SetFloat(bump)

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

    if diffuse_hsv is not None:
        dif_hsv = tree.CreateNode('hsv2')
        dif_hsv.SetName('HSV2')
        dif_hsv.SetLocation(node_column_2_x, node_column_2_y)
        dif_hsv.InputByInternalName('Hue').SetFloat(diffuse_hsv[0])
        dif_hsv.InputByInternalName('Saturation').SetFloat(diffuse_hsv[1])
        dif_hsv.InputByInternalName('Value').SetFloat(diffuse_hsv[2])
        dif_hsv.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Color'))
        node_column_2_y += 130

    if diffuse_math is not None:
        dif_math = tree.CreateNode('image_map')
        dif_math.SetLocation(node_column_2_x, node_column_2_y)
        # TODO not implemented
        node_column_2_y += 130

    if diffuse_texture is not None:
        dif_map = tree.CreateNode('image_map')
        dif_map.SetName('ColorTexture')
        dif_map.SetLocation(node_column_2_x, node_column_2_y)
        dif_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + diffuse_texture)
        dif_map_out = dif_map.OutputByInternalName('Color')
        if diffuse_math is not None:
            # noinspection PyUnboundLocalVariable
            dif_map_out.ConnectToInput(dif_math.InputByInternalName('Color'))
        elif diffuse_hsv is not None:
            # noinspection PyUnboundLocalVariable
            dif_map_out.ConnectToInput(dif_hsv.InputByInternalName('Color'))
        else:
            dif_map_out.ConnectToInput(phs.InputByInternalName('Color'))
        dif_map.SetInputsCollapsed(True)
        dif_map.SetPreviewVisible(True)
        node_column_2_y += 255

    if opacity_texture is not None:
        opa_map = tree.CreateNode('image_map')
        opa_map.SetName('OpacityTexture')
        opa_map.SetLocation(node_column_2_x, node_column_2_y)
        opa_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + opacity_texture)
        opa_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Transparency'))
        if spec != (0, 0, 0):
            opa_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Specular'))
        opa_map.SetInputsCollapsed(True)
        opa_map.SetPreviewVisible(True)
        node_column_2_y += 255

    if bump_texture is not None:
        pass  # TODO

    elif 'BumpMapFromColorTexture' in shader:

        desaturator = tree.CreateNode('hsv2')
        desaturator.SetName('Desaturator')
        desaturator.SetLocation(node_column_3_x, 320)
        desaturator.InputByInternalName('Saturation').SetFloat(0)
        # noinspection PyUnboundLocalVariable
        dif_map.OutputByInternalName('Color').ConnectToInput(desaturator.InputByInternalName('Color'))

        multiplier = tree.CreateNode('color_math')
        multiplier.SetName('Multiplier')
        multiplier.SetLocation(node_column_2_x, node_column_2_y)
        multiplier.InputByInternalName('Math_Argument').SetFloat(3)
        multiplier.InputByInternalName('Value_1').SetColor(1, 1, 1)
        multiplier.InputByInternalName('Value_2').SetColor(1, 1, 1)
        desaturator.OutputByInternalName('Color').ConnectToInput(multiplier.InputByInternalName('Value_1'))
        desaturator.OutputByInternalName('Color').ConnectToInput(multiplier.InputByInternalName('Value_2'))
        multiplier.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Bump'))
        node_column_2_y += 70

    # -------------------------Cycles-Shaders-------------------------

    if mat_name in ['7_Tear', '7_EyeSurface']:
        phs.SetInputsCollapsed(True)
        cyc = tree.CreateNode('CyclesSurface')
        cyc.SetLocation(node_column_1_x, node_column_1_y)
        tree.SetRendererRootNode(poser.kRenderEngineCodeSUPERFLY, cyc)
        node_column_1_y += 130

        if mat_name == '7_EyeSurface':
            clo1 = tree.CreateNode('ccl_MixClosure')
            clo1.SetLocation(node_column_1_x, node_column_1_y)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            math = tree.CreateNode('ccl_Math')
            math.SetLocation(node_column_2_x, node_column_2_y)
            math.InputByInternalName('Type').SetFloat(1)
            math.OutputByInternalName('Value').ConnectToInput(clo1.InputByInternalName('Fac'))
            node_column_2_y += 145

            light_path = tree.CreateNode('ccl_LightPath')
            light_path.SetLocation(node_column_3_x, node_column_3_y)
            light_path.OutputByInternalName('Is Shadow Ray').ConnectToInput(math.InputByInternalName('Value1'))
            light_path.OutputByInternalName('Is Diffuse Ray').ConnectToInput(math.InputByInternalName('Value2'))

            glass_bsdf = tree.CreateNode('ccl_GlassBsdf')
            glass_bsdf.SetLocation(node_column_2_x, node_column_2_y)
            glass_bsdf.InputByInternalName('Color').SetColor(1, 1, 1)
            glass_bsdf.InputByInternalName('Roughness').SetFloat(0.02)
            glass_bsdf.InputByInternalName('IOR').SetFloat(1.376)
            glass_bsdf.InputByInternalName('Distribution').SetFloat(2)
            glass_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
            node_column_2_y += 145

            transparent_bsdf = tree.CreateNode('ccl_TransparentBsdf')
            transparent_bsdf.SetLocation(node_column_2_x, node_column_2_y)
            transparent_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))


        elif mat_name == '7_Tear':
            clo1 = tree.CreateNode('ccl_AddClosure')
            clo1.SetLocation(node_column_1_x, node_column_1_y)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            node_column_2_y = 232
            transparent_bsdf = tree.CreateNode('ccl_TransparentBsdf')
            transparent_bsdf.SetLocation(node_column_2_x, node_column_2_y)
            transparent_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
            node_column_2_y += 74

            refraction_bsdf = tree.CreateNode('ccl_RefractionBsdf')
            refraction_bsdf.SetLocation(node_column_2_x, node_column_2_y)
            refraction_bsdf.InputByInternalName('Color').SetColor(0.3, 0.3, 0.3)
            refraction_bsdf.InputByInternalName('IOR').SetFloat(1.33)
            refraction_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))

    # for inp in root.Inputs():
    #    print(inp.InternalName())

# - every node is 105 px wide.
# - CyclesSurface is 117 px tall.
