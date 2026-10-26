import poser
from typing import Any, Dict, Optional, Set, Tuple

from v4_material_loader import easy_color, find_absolute_path, get_value_for_mat


def inject_material(
        material: poser.MaterialType,
        manifest: Dict[str, Any],
        user_choices: Optional[Set[str]],
) -> Set[str]:
    """
    A manifest is a dictionary containing everything special about the appearance of your character.

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
    - Glossy [float]: Cycles only
    - GlossyRoughness [float]: Cycles only
    - OpacityTexture [str-path]
    - Roughness [float]
    - Specular [color]
    - SpecularTexture [str-path]
    - Metallic [float]
    - Emissive [float]
    - Bump [float]
    - BumpTexture [str-path]
    - BumpMapIsColorTexture [bool]
    - BumpMapFromColorTexture [bool]
    - Normal [float]
    - NormalTexture [str-path]
    - Displacement [float]
    - DisplacementTexture [str-path]
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
        Face: 0.05
        Lips: 0.025
      ```

    :returns: a Set containing the previous choices of the user
    """

    mat_name = material.Name()
    if mat_name not in [
        'Arms', 'Cornea', 'Ears', 'EyeMoisture', 'EyeMoisture_Genesis_8_Female_Eyelashes', 'EyeSocket',
        'Eyelashes', 'Face', 'Fingernails', 'Irises', 'Legs', 'Lips', 'Mouth', 'Preview', 'Pupils',
        'Sclera', 'Teeth', 'Toenails', 'Torso']:
        return user_choices

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
    if mat_name in ['Preview']:
        phs.SetInputsCollapsed(True)
        phs.SetPreviewVisible(True)
    node_column_1_y += 90

    # ------------------------Parse-Manifest--------------------------

    shader = get_shader(mat_name, manifest)
    chosen_mode = 0

    # color
    color = (1, 1, 1)
    if mat_name in ['Preview']:
        color = (0, 0, 0)
    elif 'Color' in shader:
        color = easy_color(get_value_for_mat(shader['Color'], mat_name, chosen_mode, color))
    elif mat_name in ['Eyelashes', 'Pupils']:  # do not merge into the above list
        color = (0, 0, 0)

    # color texture
    diffuse_texture: Optional[str] = None
    diffuse_math_argument, diffuse_math_value1, diffuse_math_value2, diffuse_math_name = None, None, None, None
    diffuse_hue, diffuse_saturation, diffuse_brightness = None, None, None
    diffuse_hsv: Optional[Tuple] = None
    if 'ColorTexture' in shader:
        diffuse_texture = get_value_for_mat(shader['ColorTexture'], mat_name, chosen_mode, None)
        if diffuse_texture == 'null': diffuse_texture = None

    if diffuse_texture is not None:
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

    # opacity texture
    opacity_texture: Optional[str] = None
    if 'OpacityTexture' in shader:
        opacity_texture = get_value_for_mat(shader['OpacityTexture'], mat_name, chosen_mode, None)
        if opacity_texture == 'null': opacity_texture = None

    # opacity
    opacity = 0
    if mat_name in ['Cornea', 'EyeMoisture', 'EyeMoisture_Genesis_8_Female_Eyelashes', 'Preview'] or \
            opacity_texture is not None:
        opacity = 1

    # diffuse roughness
    rough = 0
    if 'Roughness' in shader:
        rough = float(get_value_for_mat(shader['Roughness'], mat_name, chosen_mode, rough))

    # specular texture
    specular_texture: Optional[str] = None
    if 'SpecularTexture' in shader:
        specular_texture = get_value_for_mat(shader['SpecularTexture'], mat_name, chosen_mode, None)
        if specular_texture == 'null': specular_texture = None

    # metallic
    metal = 0
    if mat_name in ['7_EyeSurface', '7_Tear']:
        if mat_name == '7_EyeSurface':
            metal = 0.04
        elif mat_name == '7_Tear':
            metal = 0.1
    elif 'Metallic' in shader:
        metal = float(get_value_for_mat(shader['Metallic'], mat_name, chosen_mode, metal))

    # emissive
    emissive = 0
    if 'Emissive' in shader:
        emissive = float(get_value_for_mat(shader['Emissive'], mat_name, chosen_mode, emissive))

    # bump
    bump = 0
    if 'Bump' in shader:
        bump = float(get_value_for_mat(shader['Bump'], mat_name, chosen_mode, bump)) * 0.3937

    # bump texture
    bump_texture: Optional[str] = None
    bump_map_is_color_texture, bump_map_from_color_texture = False, False
    if 'BumpTexture' in shader:
        bump_texture = get_value_for_mat(shader['BumpTexture'], mat_name, chosen_mode, None)
    elif 'BumpMapIsColorTexture' in shader:
        bump_map_is_color_texture = \
            get_value_for_mat(shader['BumpMapIsColorTexture'], mat_name, chosen_mode, bump) == 'true'
    elif 'BumpMapFromColorTexture' in shader:
        bump_map_from_color_texture = \
            get_value_for_mat(shader['BumpMapFromColorTexture'], mat_name, chosen_mode, bump) == 'true'
    if bump_texture == 'null': bump_texture = None

    # normal texture
    normal_texture: Optional[str] = None
    if 'NormalTexture' in shader:
        normal_texture = get_value_for_mat(shader['NormalTexture'], mat_name, chosen_mode, None)
        if normal_texture == 'null': normal_texture = None

    # normal
    normal = 0
    if 'Normal' in shader:
        normal = float(get_value_for_mat(shader['Normal'], mat_name, chosen_mode, normal))
    elif normal_texture is not None:
        normal = 1

    # displacement
    displacement = 0
    if 'Displacement' in shader:
        displacement = float(get_value_for_mat(shader['Displacement'], mat_name, chosen_mode, bump)) * 0.3937

    # displacement texture
    displacement_texture: Optional[str] = None
    if 'DisplacementTexture' in shader:
        displacement_texture = get_value_for_mat(
            shader['DisplacementTexture'], mat_name, chosen_mode, None)
        if displacement_texture == 'null': displacement_texture = None

    # SSS radii
    sss_radii = None
    if 'ScatterRadius' in shader:
        sss_radii = get_value_for_mat(shader['ScatterRadius'], mat_name, chosen_mode, None)
    if sss_radii is not None:
        if ',' in sss_radii:
            spl = sss_radii.split(',')
            sss_radii = (float(spl[0].strip()), float(spl[1].strip()), float(spl[2].strip()))
        else:
            sss_radii = (float(sss_radii.strip()), float(sss_radii.strip()), float(sss_radii.strip()))

    # SSS scale
    sss_scale = None
    if 'ScatterScale' in shader:
        sss_scale = get_value_for_mat(shader['ScatterScale'], mat_name, chosen_mode, None)

    # SSS group
    sss_group = 1
    if mat_name in ['Fingernails', 'Toenails']:
        sss_group = 2
    elif mat_name == 'Mouth':
        sss_group = 3

    # glossy
    glossy: Optional[Tuple] = None
    glossy_roughness: Optional[float] = None
    if 'Glossy' in shader:
        glossy = get_value_for_mat(shader['Glossy'], mat_name, chosen_mode, None)
        glossy_roughness = get_value_for_mat(shader['GlossyRoughness'], mat_name, chosen_mode, None)

    # -----------------------Preview-Renderer-------------------------

    material.SetAmbientColor(0, 0, 0)
    material.SetAmbientMapFileName(None)
    material.SetBumpMapFileName(find_absolute_path(bump_texture))
    material.SetBumpStrength(bump)
    material.SetDiffuseColor(*color)
    material.SetNs(0)
    # Ns is an exponent used in the calculation of the specular highlight.
    # A higher exponent results in a smaller highlight and vice versa.
    material.SetReflectionColor(0, 0, 0)
    material.SetReflectionMapFileName(None)
    material.SetReflectionStrength(0)
    material.SetSpecularColor(0, 0, 0)
    material.SetSpecularMapFileName(find_absolute_path(specular_texture))
    material.SetTextureColor(*color)
    material.SetTextureMapFileName(find_absolute_path(diffuse_texture))
    material.SetTransparencyMapFileName(find_absolute_path(opacity_texture))
    material.SetTransparencyMax(opacity)
    material.SetTransparencyMin(opacity)

    # -----------------------PhysicalSurface--------------------------

    # PhysicalSurface : Color
    phs.InputByInternalName('Color').SetColor(*color)

    # PhysicalSurface : Transparency
    phs.InputByInternalName('Transparency').SetFloat(opacity)
    if opacity_texture is not None:
        phs.InputByInternalName('TransparencyMode').SetFloat(1)

    # PhysicalSurface : Roughness
    phs.InputByInternalName('Roughness').SetFloat(rough)

    # PhysicalSurface : Specular
    spec = (0, 0, 0)
    if mat_name in ['Cornea', 'EyeMoisture']:
        spec = (0.5, 0.5, 0.5)
    elif mat_name == 'EyeMoisture_Genesis_8_Female_Eyelashes':
        spec = (1, 1, 1)
    elif 'Specular' in shader:
        spec = easy_color(get_value_for_mat(shader['Specular'], mat_name, chosen_mode, spec))
    elif specular_texture is not None:
        spec = (1, 1, 1)  # do not merge into the conditions above
    phs.InputByInternalName('Specular').SetColor(*spec)

    # PhysicalSurface : Metallic
    phs.InputByInternalName('Metallic').SetFloat(metal)

    # PhysicalSurface : Emission
    emiss = (0, 0, 0)
    if emissive != 0:
        emiss = (1, 1, 1)
        phs.InputByInternalName('EmissionStrength').SetFloat(emissive)
    phs.InputByInternalName('Emission').SetColor(*emiss)

    # PhysicalSurface : Bump
    phs.InputByInternalName('Bump').SetFloat(bump)

    # PhysicalSurface : NormalMap
    phs.InputByInternalName('NormalMap').SetFloat(normal)

    # PhysicalSurface : Displacement
    phs.InputByInternalName('Displacement').SetFloat(displacement)

    # PhysicalSurface : SSS Radii
    if sss_radii is not None:
        phs.InputByInternalName('ScatterDistR').SetFloat(sss_radii[0])
        phs.InputByInternalName('ScatterDistG').SetFloat(sss_radii[1])
        phs.InputByInternalName('ScatterDistB').SetFloat(sss_radii[2])

    # PhysicalSurface : SSS Scale
    if sss_scale is not None:
        phs.InputByInternalName('Scatter_Scale').SetFloat(float(sss_scale))

    # PhysicalSurface : SSS Defaults
    phs.InputByInternalName('Scatter_Group').SetFloat(sss_group)
    phs.InputByInternalName('SSSMethod').SetFloat(1)

    # -------------------------Dependencies---------------------------

    def jump_to_next_column_if_necessary():
        nonlocal node_column_2_x, node_column_2_y, node_column_3_x
        if node_column_2_y > 350:
            node_column_2_x += 225
            node_column_3_x += 225
            node_column_2_y = 20

    if diffuse_hsv is not None:
        dif_hsv = tree.CreateNode('hsv2')
        dif_hsv.SetName('HSV2')
        dif_hsv.SetLocation(node_column_2_x, node_column_2_y)
        dif_hsv.InputByInternalName('Hue').SetFloat(diffuse_hsv[0])
        dif_hsv.InputByInternalName('Saturation').SetFloat(diffuse_hsv[1])
        dif_hsv.InputByInternalName('Value').SetFloat(diffuse_hsv[2])
        dif_hsv_out = dif_hsv.OutputByInternalName('Color')
        dif_hsv_out.ConnectToInput(phs.InputByInternalName('Color'))
        if emiss != (0, 0, 0):
            dif_hsv_out.ConnectToInput(phs.InputByInternalName('Emission'))
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
            if emiss != (0, 0, 0):
                dif_math_out.ConnectToInput(phs.InputByInternalName('Emission'))
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
            if emiss != (0, 0, 0):
                dif_map_out.ConnectToInput(phs.InputByInternalName('Emission'))
        if bump_map_is_color_texture:
            dif_map_out.ConnectToInput(phs.InputByInternalName('Bump'))
        dif_map.SetInputsCollapsed(True)
        dif_map.SetPreviewVisible(True)
        node_column_2_y += 255
        jump_to_next_column_if_necessary()

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
        jump_to_next_column_if_necessary()

    if specular_texture is not None:
        spc_map = tree.CreateNode('image_map')
        spc_map.SetName('SpecularTexture')
        spc_map.SetLocation(node_column_2_x, node_column_2_y)
        spc_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + specular_texture)
        spc_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Specular'))
        spc_map.SetInputsCollapsed(True)
        spc_map.SetPreviewVisible(True)
        node_column_2_y += 255
        jump_to_next_column_if_necessary()

    if bump_texture is not None:
        bmp_map = tree.CreateNode('image_map')
        bmp_map.SetName('BumpTexture')
        bmp_map.SetLocation(node_column_2_x, node_column_2_y)
        bmp_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + bump_texture)
        bmp_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Bump'))
        bmp_map.SetInputsCollapsed(True)
        bmp_map.SetPreviewVisible(True)
        node_column_2_y += 255
        jump_to_next_column_if_necessary()

    elif bump_map_from_color_texture:

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

    if normal_texture is not None:
        nrm_map = tree.CreateNode('image_map')
        nrm_map.SetName('NormalTexture')
        nrm_map.SetLocation(node_column_2_x, node_column_2_y)
        nrm_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + normal_texture)
        nrm_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('NormalMap'))
        nrm_map.SetInputsCollapsed(True)
        nrm_map.SetPreviewVisible(True)
        node_column_2_y += 255
        jump_to_next_column_if_necessary()

    if displacement_texture is not None:
        dsp_map = tree.CreateNode('image_map')
        dsp_map.SetName('DisplacementTexture')
        dsp_map.SetLocation(node_column_2_x, node_column_2_y)
        dsp_map.InputByInternalName('Image_Source').SetString(':Runtime:Texture:' + displacement_texture)
        dsp_map.OutputByInternalName('Color').ConnectToInput(phs.InputByInternalName('Displacement'))
        dsp_map.SetInputsCollapsed(True)
        dsp_map.SetPreviewVisible(True)
        node_column_2_y += 255
        jump_to_next_column_if_necessary()

    # -------------------------Cycles-Shaders-------------------------

    if mat_name in ['Cornea', 'EyeMoisture', 'EyeMoisture_Genesis_8_Female_Eyelashes'] or glossy is not None:
        phs.SetInputsCollapsed(True)
        cyc = tree.CreateNode('CyclesSurface')
        cyc.SetLocation(node_column_1_x, node_column_1_y)
        tree.SetRendererRootNode(poser.kRenderEngineCodeSUPERFLY, cyc)
        node_column_1_y += 130

        if glossy is not None:
            clo1 = tree.CreateNode('ccl_AddClosure')
            clo1.SetLocation(node_column_1_x, node_column_1_y)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            if 'ScatterRadius' not in shader:
                color_bsdf = tree.CreateNode('ccl_DiffuseBsdf')
                color_bsdf.SetLocation(node_column_3_x, node_column_3_y)
                color_bsdf.InputByInternalName('Color').SetColor(*color)
                color_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
                node_column_3_y += 110

            else:
                color_bsdf = tree.CreateNode('ccl_SubsurfaceScattering')
                color_bsdf.SetLocation(node_column_3_x, node_column_3_y)
                color_bsdf.InputByInternalName('Color').SetColor(*color)
                if sss_scale is not None:
                    color_bsdf.InputByInternalName('Scale').SetFloat(float(sss_scale))
                color_bsdf.InputByInternalName('Radius').SetColor(sss_radii[0], sss_radii[1], sss_radii[2])
                color_bsdf.InputByInternalName('Scatter Group ID').SetFloat(sss_group)
                color_bsdf.InputByInternalName('Method').SetFloat(0)
                color_bsdf.OutputByInternalName('BSSRDF').ConnectToInput(clo1.InputByInternalName('Closure1'))
                node_column_3_y += 210

            diffuse_color = None
            if diffuse_hsv is not None:
                diffuse_color = dif_hsv_out
            elif diffuse_math_argument is not None:
                diffuse_color = dif_math_out
            elif diffuse_texture is not None:
                diffuse_color = dif_map_out
            if diffuse_color is not None:
                diffuse_color.ConnectToInput(color_bsdf.InputByInternalName('Color'))

            glossy_bsdf = tree.CreateNode('ccl_GlossyBsdf')
            glossy_bsdf.SetLocation(node_column_3_x, node_column_3_y)
            glossy_bsdf.InputByInternalName('Color').SetColor(*easy_color(glossy))
            if glossy_roughness is not None:
                glossy_bsdf.InputByInternalName('Roughness').SetFloat(float(glossy_roughness))
            glossy_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))

        elif mat_name in ['Cornea', 'EyeMoisture']:
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


        elif mat_name == 'EyeMoisture_Genesis_8_Female_Eyelashes':
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

    return user_choices


def get_shader(mat_name: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
    shader: Dict[str, Any] = {}
    try:
        shader = manifest[mat_name]
    except KeyError:
        pass

    # merge super-shaders into sub-shaders
    if 'Skin' in manifest and mat_name in ['Arms', 'Ears', 'EyeSocket', 'Face', 'Legs', 'Lips', 'Torso']:
        shader = {**manifest['Skin'], **shader}
    if 'Face' in manifest and mat_name in ['Ears', 'EyeSocket', 'Face', 'Lips']:
        shader = {**manifest['Face'], **shader}
    if 'Eyes' in manifest and mat_name in ['Irises', 'Sclera']:
        # shader |= manifest['Eyes']  # Python 3.9
        shader = {**manifest['Eyes'], **shader}
    if 'Arms' in manifest and mat_name in ['Fingernails', 'Toenails']:
        shader = {**manifest['Arms'], **shader}
    if 'Nails' in manifest and mat_name in ['Fingernails', 'Toenails']:
        shader = {**manifest['Nails'], **shader}
    if 'Mouth' in manifest and mat_name == 'Teeth':
        shader = {**manifest['Mouth'], **shader}

    return shader
