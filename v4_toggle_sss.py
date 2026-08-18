from typing import Dict, List, Tuple

import poser

SSS_DEFINITIONS: Dict[str, List[Tuple]] = {
    'ESPINELA': [(0.35, 0.3, 0.2, 0.0), (0.2, 0.39, 0.5, 1.0), (0.4, 0.2, 0.1)],
    'LUNA': [(0.4, 0.3, 0.2, 0.0), (0.25, 0.39, 0.5, 1.0), (0.4, 0.2, 0.1)],
}

scene = poser.Scene()
figure = scene.CurrentFigure()

get_material = lambda mat: figure.Material(mat).ShaderTree() \
    .RendererRootNode(poser.kRenderEngineCodeSUPERFLY)
get_value = lambda mat, inp: mat.InputByInternalName(inp).Value()

base = get_material('2_SkinTorso')
overall_sss = (get_value(base, 'ScatterDistR') + get_value(base, 'ScatterDistG') +
               get_value(base, 'ScatterDistB'))
turn_sss_on = overall_sss == 0.0

definition = SSS_DEFINITIONS[figure.Name()]
for material in ['1_EyeSocket', '1_Lip', '1_Nostril', '1_SkinFace', '2_Nipple', '2_SkinHead',
                 '2_SkinHip', '2_SkinNeck', '2_SkinTorso', '3_Fingernail', '3_SkinArm', '3_SkinFoot',
                 '3_SkinForearm', '3_SkinHand', '3_SkinLeg', '3_Toenail']:
    phs = get_material(material)

    select_tuple_item = 0
    if material == '1_Lip': select_tuple_item = 1  # lips with makeup
    if material in ['3_Fingernail', '3_Toenail']:
        if get_value(phs, 'Roughness') == definition[0][3] and \
                get_value(phs, 'Specular')[0] == definition[1][3]:
            continue  # do not alter nails with makeup
        select_tuple_item = 2  # nails with NO makeup

    phs.InputByInternalName('Roughness').SetFloat(definition[0][select_tuple_item] if turn_sss_on else 0.0)
    spec = definition[1][select_tuple_item] if turn_sss_on else 0.0
    phs.InputByInternalName('Specular').SetColor(spec, spec, spec)
    phs.InputByInternalName('ScatterDistR').SetFloat(definition[2][0] if turn_sss_on else 0.0)
    phs.InputByInternalName('ScatterDistG').SetFloat(definition[2][1] if turn_sss_on else 0.0)
    phs.InputByInternalName('ScatterDistB').SetFloat(definition[2][2] if turn_sss_on else 0.0)
    phs.InputByInternalName('SSSMethod').SetFloat(1.0)  # Random Walk (Burley is 3.0)
