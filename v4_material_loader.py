import poser
from typing import Any, Dict, Optional, Set, Tuple


def inject_material(
        material: poser.MaterialType,
        manifest: Dict[str, Any],
        user_choices: Optional[Set[str]],
) -> Set[str]:
    """
    A manifest is a dictionary containing everything special about the appearance of your character.
    It contains these shader names as its keys:

    - Skin (a superset for Face, Lips, Torso and Limbs excluding nails)
    - Face (a superset for Lips)
    - Eyelashes
    - Eyes (a superset for Lacrimal)
    - Lacrimal
    - Lips
    - Mouth
    - Torso
    - Limbs (a superset for Nails)
    - Nails

    Every shader can have any of these parameters:

    - Modes [list]
    - DefaultMode [int]
    - Color [color]
    - ColorTexture [str-path]
    - DiffuseHue [float]: Hue in HSV2 for ColorTexture
    - DiffuseSaturation [float]: Saturation in HSV2 for ColorTexture
    - DiffuseBrightness [float]: Value in HSV2 for ColorTexture
    - DiffuseMathArgument [str]: color_math for ColorTexture, e.g. Add,Subtract,Multiple,Divide,Min,Max
    - DiffuseMathValue1 [color]: color_math for ColorTexture, leave undefined to input ColorTexture
    - DiffuseMathValue2 [color]: color_math for ColorTexture, leave undefined to input ColorTexture
    - DiffuseMathName [str]: a visible name for the color_math node
    - OpacityTexture [str-path]
    - Roughness [float]
    - Specular [color]
    - Bump [float]
    - BumpTexture [str-path]
    - BumpMapIsColorTexture [bool]
    - BumpMapFromColorTexture [bool]
    - ScatterRadius [str: "<float>, <float>, <float>"]
    - ScatterScale [float]

    And each parameter can have these types of inputs:

    - raw values; e.g. `Bump: 0.05`
    - list of values; e.g.
      ```
      Bump:
        - 0.05   # for mode 1
        - 0.025  # for mode 2
      ```
    - dictionary of values for each V4 material; e.g.
      ```
      Bump:
        SkinFace: 0.05
        Lip: 0.025
      ```

    :returns: a Set containing the previous choices of the user
    """

    mat_name = material.Name()
    tree = material.ShaderTree()
    previous_nodes = tree.Nodes()
    phs = tree.CreateNode('PhysicalSurface')
    for previous_node in previous_nodes:
        tree.DeleteNode(previous_node)

    node_column_1_x, node_column_2_x, node_column_3_x = 20, 245, 470
    node_column_1_y, node_column_2_y, node_column_3_y = 20, 20, 20

    phs.SetName('PhysicalSurface')
    phs.SetLocation(node_column_1_x, node_column_1_y)
    tree.SetRendererRootNode(poser.kRenderEngineCodeFIREFLY, phs)
    if mat_name in ['1_Eyebrow', 'Invis', 'Pubic_Hair', 'Preview']:
        phs.SetInputsCollapsed(True)
        phs.SetPreviewVisible(True)
    node_column_1_y += 90

    # ------------------------Parse-Manifest--------------------------

    shader_name, shader = get_shader(mat_name, manifest)

    chosen_mode = 0
    if user_choices is None:
        if 'DefaultMode' in shader:
            chosen_mode = int(shader['DefaultMode']) - 1
    elif 'Modes' in shader:
        if len(shader['Modes']) == 1:
            chosen_mode = 0
        else:
            found_a_choice = False
            for choice in user_choices:
                if choice in shader['Modes']:
                    chosen_mode = shader['Modes'].index(choice)
                    found_a_choice = True
            if not found_a_choice:
                choice = poser.DialogSimple.AskMenu(
                    'Character Material Selector', shader_name, tuple(shader['Modes']))
                if choice is not None and len(choice) > 0:
                    user_choices.add(choice)
                    chosen_mode = shader['Modes'].index(choice)

    diffuse_texture: Optional[str] = None
    diffuse_math_argument, diffuse_math_value1, diffuse_math_value2, diffuse_math_name = None, None, None, None
    diffuse_hue, diffuse_saturation, diffuse_brightness = None, None, None
    diffuse_hsv: Optional[Tuple] = None
    if 'ColorTexture' in shader:
        diffuse_texture = get_value_for_mat(shader['ColorTexture'], mat_name, chosen_mode, None)
        if diffuse_texture == 'null': diffuse_texture = None

        if 'DiffuseMathArgument' in shader:
            diffuse_math_argument = get_value_for_mat(
                shader['DiffuseMathArgument'], mat_name, chosen_mode, None)
            if 'DiffuseMathValue1' in shader:
                diffuse_math_value1 = easy_color(get_value_for_mat(
                    shader['DiffuseMathValue1'], mat_name, chosen_mode, None))
            if 'DiffuseMathValue2' in shader:
                diffuse_math_value2 = easy_color(get_value_for_mat(
                    shader['DiffuseMathValue2'], mat_name, chosen_mode, None))
            if 'DiffuseMathName' in shader:
                diffuse_math_name = get_value_for_mat(
                    shader['DiffuseMathName'], mat_name, chosen_mode, None)

        if 'DiffuseHue' in shader:
            diffuse_hue = get_value_for_mat(shader['DiffuseHue'], mat_name, chosen_mode, None)
        if 'DiffuseSaturation' in shader:
            diffuse_saturation = get_value_for_mat(
                shader['DiffuseSaturation'], mat_name, chosen_mode, None)
        if 'DiffuseBrightness' in shader:
            diffuse_brightness = get_value_for_mat(
                shader['DiffuseBrightness'], mat_name, chosen_mode, None)
        if diffuse_hue is not None or diffuse_saturation is not None or diffuse_brightness is not None:
            diffuse_hsv = (float(diffuse_hue) if diffuse_hue is not None else 0,
                           float(diffuse_saturation) if diffuse_saturation is not None else 1,
                           float(diffuse_brightness) if diffuse_brightness is not None else 1)

    opacity_texture: Optional[str] = None
    if 'OpacityTexture' in shader:
        opacity_texture = get_value_for_mat(shader['OpacityTexture'], mat_name, chosen_mode, None)

    bump_texture: Optional[str] = None
    if 'BumpTexture' in shader:
        bump_texture = get_value_for_mat(shader['BumpTexture'], mat_name, chosen_mode, None)

    # -----------------------PhysicalSurface--------------------------

    # PhysicalSurface : Color
    color = (1, 1, 1)
    if mat_name in ['1_Eyebrow', '5_Cornea', '5_Pupil', 'Invis', 'Pubic_Hair', 'Preview']:
        color = (0, 0, 0)
    elif 'Color' in shader:
        color = easy_color(get_value_for_mat(shader['Color'], mat_name, chosen_mode, color))
    elif mat_name in ['6_Eyelash']:  # do not merge into the above list
        color = (0, 0, 0)
    phs.InputByInternalName('Color').SetColor(*color)

    # PhysicalSurface : Transparency
    trans = 0
    if mat_name in ['5_Cornea', '7_EyeSurface', '7_Tear', 'Invis', 'Pubic_Hair', 'Preview'] or \
            opacity_texture is not None:
        trans = 1
    phs.InputByInternalName('Transparency').SetFloat(trans)
    if opacity_texture is not None:
        phs.InputByInternalName('TransparencyMode').SetFloat(1)

    # PhysicalSurface : Roughness
    rough = 0
    if 'Roughness' in shader:
        rough = float(get_value_for_mat(shader['Roughness'], mat_name, chosen_mode, rough))
    phs.InputByInternalName('Roughness').SetFloat(rough)

    # PhysicalSurface : Specular
    spec = (0, 0, 0)
    if mat_name == '7_EyeSurface':
        spec = (0.5, 0.5, 0.5)
    elif mat_name == '7_Tear':
        spec = (1, 1, 1)
    elif 'Specular' in shader:
        spec = easy_color(get_value_for_mat(shader['Specular'], mat_name, chosen_mode, spec))
    phs.InputByInternalName('Specular').SetColor(*spec)

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
        bump = float(get_value_for_mat(shader['Bump'], mat_name, chosen_mode, bump)) * 0.3937
    phs.InputByInternalName('Bump').SetFloat(bump)

    # PhysicalSurface : SSS Radii
    sss_radii = None
    if 'ScatterRadius' in shader:
        if shader_name == 'Eyes' and mat_name != '5_Sclera':
            pass
        else:
            sss_radii = get_value_for_mat(shader['ScatterRadius'], mat_name, chosen_mode, None)
    elif mat_name == '5_Cornea':
        eyes_shader = get_shader('5_Sclera', manifest)[1]
        if 'ScatterRadius' in eyes_shader:
            sss_radii = get_value_for_mat(
                eyes_shader['ScatterRadius'], '5_Sclera', chosen_mode, None)
    if sss_radii is not None:
        spl = sss_radii.split(',')
        phs.InputByInternalName('ScatterDistR').SetFloat(float(spl[0].strip()))
        phs.InputByInternalName('ScatterDistG').SetFloat(float(spl[1].strip()))
        phs.InputByInternalName('ScatterDistB').SetFloat(float(spl[2].strip()))

    # PhysicalSurface : SSS Scale
    sss_scale = None
    if 'ScatterScale' in shader:
        if shader_name == 'Eyes' and mat_name != '5_Sclera':
            pass
        else:
            sss_scale = get_value_for_mat(shader['ScatterScale'], mat_name, chosen_mode, None)
    elif mat_name == '5_Cornea':
        eyes_shader = get_shader('5_Sclera', manifest)[1]
        if 'ScatterScale' in eyes_shader:
            sss_scale = get_value_for_mat(
                eyes_shader['ScatterScale'], '5_Sclera', chosen_mode, None)
    if sss_scale is not None:
        phs.InputByInternalName('Scatter_Scale').SetFloat(float(sss_scale))

    # PhysicalSurface : SSS Defaults
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

    if diffuse_math_argument is not None:
        dif_math = tree.CreateNode('color_math')
        if diffuse_math_name is not None:
            dif_math.SetName(diffuse_math_name)
        dif_math.SetLocation(node_column_2_x, node_column_2_y)
        dif_math.InputByInternalName('Math_Argument').SetFloat(
            {
                'Add': 1,
                'Subtract': 2,
                'Multiply': 3,
                'Divide': 4,
                'Min': 15,
                'Max': 16,
            }[diffuse_math_argument]
        )
        if diffuse_math_value1 is not None:
            dif_math.InputByInternalName('Value_1').SetColor(*diffuse_math_value1)
        if diffuse_math_value2 is not None:
            dif_math.InputByInternalName('Value_2').SetColor(*diffuse_math_value2)
        dif_math_out = dif_math.OutputByInternalName('Color')
        if diffuse_hsv is None:
            dif_math_out.ConnectToInput(phs.InputByInternalName('Color'))
        else:
            dif_math_out.ConnectToInput(dif_hsv.InputByInternalName('Color'))
        node_column_2_y += 114

    if diffuse_texture is not None:
        dif_map = tree.CreateNode('image_map')
        dif_map.SetName('ColorTexture')
        dif_map.SetLocation(node_column_2_x, node_column_2_y)
        dif_map.InputByInternalName('Image_Source').SetString(':Runtime:Textures:' + diffuse_texture)
        dif_map_out = dif_map.OutputByInternalName('Color')
        if diffuse_math_argument is not None:
            if diffuse_math_value1 is None:
                dif_map_out.ConnectToInput(dif_math.InputByInternalName('Value_1'))
            if diffuse_math_value2 is None:
                dif_map_out.ConnectToInput(dif_math.InputByInternalName('Value_2'))
        elif diffuse_hsv is not None:
            dif_map_out.ConnectToInput(dif_hsv.InputByInternalName('Color'))
        else:
            dif_map_out.ConnectToInput(phs.InputByInternalName('Color'))
        if 'BumpMapIsColorTexture' in shader:
            dif_map_out.ConnectToInput(phs.InputByInternalName('Bump'))
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
        bmp_map = tree.CreateNode('image_map')
        bmp_map.SetName('BumpTexture')
        bmp_map.SetLocation(node_column_2_x, node_column_2_y)
        bmp_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + bump_texture)
        bmp_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Bump'))
        bmp_map.SetInputsCollapsed(True)
        bmp_map.SetPreviewVisible(True)
        node_column_2_y += 255

    elif 'BumpMapFromColorTexture' in shader:

        desaturator = tree.CreateNode('hsv2')
        desaturator.SetName('Desaturator')
        desaturator.SetLocation(node_column_3_x, 320)
        desaturator.InputByInternalName('Saturation').SetFloat(0)
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
        node_column_2_y += 114

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

    # for inp in phs.Inputs():
    #    print(inp.InternalName())

    # - every node is 105 px wide.
    # - CyclesSurface is 117 px tall.

    return user_choices


def get_shader(mat_name: str, manifest: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    shader: Dict[str, Any] = {}
    shader_name: str = ''

    # find the correct shader based on the material name
    try:
        shader_name = {
            '1_EyeSocket': 'Face',
            '1_Lip': 'Lips',
            '1_Nostril': 'Face',
            '1_SkinFace': 'Face',
            '2_Nipple': 'Torso',
            '2_SkinHead': 'Torso',
            '2_SkinNeck': 'Torso',
            '2_SkinTorso': 'Torso',
            '2_SkinHip': 'Torso',
            '3_Fingernail': 'Nails',
            '3_SkinArm': 'Limbs',
            '3_SkinFoot': 'Limbs',
            '3_SkinForearm': 'Limbs',
            '3_SkinHand': 'Limbs',
            '3_SkinLeg': 'Limbs',
            '3_Toenail': 'Nails',
            '4_InnerMouth': 'Mouth',
            '4_Gums': 'Mouth',
            '4_Teeth': 'Mouth',
            '4_Tongue': 'Mouth',
            '5_Iris': 'Eyes',
            '5_Lacrimal': 'Lacrimal',
            '5_Sclera': 'Eyes',
            '6_Eyelash': 'Eyelashes',

            'Gen_Skin': 'Penis',
            'Glans': 'Penis',
        }[mat_name]
        shader = manifest[shader_name]
    except KeyError:
        pass

    # merge super-shaders into sub-shaders
    if 'Skin' in manifest and \
            (mat_name in ['1_EyeSocket', '1_Lip', '1_Nostril', '1_SkinFace',
                          '3_SkinArm', '3_SkinForearm', '3_SkinHand', '3_SkinLeg']
             or mat_name.startswith('2_')):
        shader = {**manifest['Skin'], **shader}
    if 'Eyes' in manifest and mat_name == '5_Lacrimal':
        # shader |= manifest['Eyes']  # Python 3.9
        shader = {**manifest['Eyes'], **shader}
    if 'Face' in manifest and mat_name == '1_Lip':
        shader = {**manifest['Face'], **shader}
    if 'Limbs' in manifest and mat_name in ['3_Fingernail', '3_Toenail']:
        shader = {**manifest['Limbs'], **shader}

    return shader_name, shader


def get_value_for_mat(
        user_input: Any,
        mat_name: str,
        chosen_mode: int,
        default: Any
) -> Any:  # float | str

    if isinstance(user_input, dict):
        for easy_name, value in user_input.items():
            if ', ' in easy_name:
                for easier_name in easy_name.split(', '):
                    if compare_easy_mat_name(easier_name, mat_name):
                        if isinstance(value, list):
                            return value[chosen_mode]
                        else:
                            return value
            if easy_name.lower() == 'else' or compare_easy_mat_name(easy_name, mat_name):
                if isinstance(value, list):
                    return value[chosen_mode]
                else:
                    return value
        return default
    elif isinstance(user_input, list):
        return user_input[chosen_mode]
    else:
        return user_input


def compare_easy_mat_name(easy_name: str, mat_name: str) -> bool:
    if easy_name.lower() == mat_name.lower(): return True
    if easy_name.lower() == mat_name[2:].lower(): return True
    if easy_name.lower() + 's' == mat_name[2:].lower(): return True
    if (easy_name.lower() == 'nail' or easy_name.lower() == 'nails') and \
            (mat_name == '3_Fingernail' or mat_name == '3_Toenail'): return True
    return False


def easy_color(any_str: Any) -> Tuple[float, float, float]:
    if not isinstance(any_str, str):
        return any_str  # can sometimes be the defaulted tuple which is already converted into a color
    try:
        return float(any_str), float(any_str), float(any_str)
    except ValueError:
        pass
    if ', ' in any_str:
        spl = any_str.split(', ')
        return float(spl[0]) / 255.0, float(spl[1]) / 255.0, float(spl[2]) / 255.0
    if any_str.startswith('0x'):
        any_str = any_str.replace('#', '').replace('0x', '')
        return int(any_str[0:2], 16) / 255.0, int(any_str[2:4], 16) / 255.0, int(any_str[4:6], 16) / 255.0
    return 0, 0, 0
