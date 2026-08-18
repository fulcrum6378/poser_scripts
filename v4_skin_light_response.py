import poser

scene = poser.Scene()
figure = scene.CurrentFigure()

get_material = lambda mat: figure.Material(mat).ShaderTree() \
    .RendererRootNode(poser.kRenderEngineCodeSUPERFLY)
get_value = lambda mat, inp: mat.InputByInternalName(inp).Value()

base = get_material('2_SkinTorso')
text_entry = poser.DialogTextEntry(
    0, '',
    f"Roughness: {get_value(base, 'Roughness'):.2f}, " +
    f"Specular: {get_value(base, 'Specular')[0]:.2f}, " +
    f"ScatterRadiusR: {get_value(base, 'ScatterDistR'):.2f}, " +
    f"ScatterRadiusG: {get_value(base, 'ScatterDistG'):.2f}, " +
    f"ScatterRadiusB: {get_value(base, 'ScatterDistB'):.2f}, " +
    f"ScatterScale: {get_value(base, 'Scatter_Scale'):.3f}"
)
if text_entry.Show() == 1:
    options = text_entry.Text().split(', ')
    option = lambda n: float(options[n].split(': ')[1])

    for material in ['1_EyeSocket', '1_Lip', '1_Nostril', '1_SkinFace', '2_Nipple', '2_SkinHead',
                     '2_SkinHip', '2_SkinNeck', '2_SkinTorso', '3_SkinArm', '3_SkinFoot',
                     '3_SkinForearm', '3_SkinHand', '3_SkinLeg']:
        phs = get_material(material)
        phs.InputByInternalName('Roughness').SetFloat(option(0))
        spec = option(1)
        phs.InputByInternalName('Specular').SetColor(spec, spec, spec)
        phs.InputByInternalName('ScatterDistR').SetFloat(option(2))
        phs.InputByInternalName('ScatterDistG').SetFloat(option(3))
        phs.InputByInternalName('ScatterDistB').SetFloat(option(4))
        phs.InputByInternalName('Scatter_Scale').SetFloat(option(5))

    scene.Draw()
