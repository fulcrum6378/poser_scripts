import os
import poser
from typing import Optional

import quick_yaml

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
manifest = quick_yaml.load(open(manifest_path, 'r').read())['Materials']

for mat in figure.Materials():
    mat_name = mat.Name()
    if mat_name != '7_Tear': continue  # TODO REMOVE

    tree = mat.ShaderTree()
    previous_nodes = tree.Nodes()
    phs = tree.CreateNode('PhysicalSurface')
    for previous_node in previous_nodes:
        tree.DeleteNode(previous_node)

    phs.SetName('PhysicalSurface')
    phs.SetLocation(20, 20)

    # -------------------------Dependencies---------------------------

    # -----------------------PhysicalSurface--------------------------

    # PhysicalSurface : Color
    in_color = phs.InputByInternalName('Color')
    if mat_name not in ['1_Eyebrow']:
        in_color.SetColor(1, 1, 1)
    else:
        in_color.SetColor(0, 0, 0)

    # PhysicalSurface : Transparency
    if mat_name in ['7_Tear']:
        phs.InputByInternalName('Transparency').SetFloat(1)

    # PhysicalSurface : Roughness
    phs.InputByInternalName('Roughness').SetFloat(0)

    # PhysicalSurface : Specular
    if mat_name in ['7_Tear']:
        phs.InputByInternalName('Specular').SetColor(1, 1, 1)
    else:
        phs.InputByInternalName('Specular').SetColor(0, 0, 0)

    # PhysicalSurface : Metallic
    if mat_name in ['7_Tear']:
        in_metallic = phs.InputByInternalName('Metallic')
        if mat_name == '7_Tear':
            in_metallic.SetFloat(0.1)

    # PhysicalSurface : Emission
    phs.InputByInternalName('Emission').SetColor(0, 0, 0)

    # PhysicalSurface : SSS
    in_sss_group = phs.InputByInternalName('Scatter_Group')
    if mat_name in ['3_Fingernail', '3_Toenail']:
        in_sss_group.SetFloat(2)
    elif mat_name in ['5_Cornea', '5_Sclera']:
        in_sss_group.SetFloat(3)
    elif mat_name in ['4_Gums', '4_InnerMouth', '4_Teeth', '4_Tongue']:
        in_sss_group.SetFloat(4)
    phs.InputByInternalName('SSSMethod').SetFloat(1)

    # -------------------------Cycles-Shaders-------------------------

    if mat_name in ['7_Tear']:
        cyc = tree.CreateNode('CyclesSurface')
        cyc.SetLocation(245, 20)

        if mat_name == '7_Tear':
            clo1 = tree.CreateNode('ccl_AddClosure')
            clo1.SetLocation(245, 150)
            clo1.OutputByInternalName('Closure').ConnectToInput(cyc.InputByInternalName('Surface'))

            transparent_bsdf = tree.CreateNode('ccl_TransparentBsdf')
            transparent_bsdf.SetLocation(245, 242)
            transparent_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure1'))

            refraction_bsdf = tree.CreateNode('ccl_RefractionBsdf')
            refraction_bsdf.SetLocation(245, 316)
            refraction_bsdf.InputByInternalName('Color').SetColor(0.3, 0.3, 0.3)
            refraction_bsdf.InputByInternalName('IOR').SetFloat(1.33)
            refraction_bsdf.OutputByInternalName('BSDF').ConnectToInput(clo1.InputByInternalName('Closure2'))

    # print(dir(root))
    # for inp in root.Inputs():
    #    print(inp.InternalName())
    # tree = poser.Scene().CurrentFigure().Material('7_Tear').ShaderTree()

# - every node is 105 px wide.
# - CyclesSurface is 117 px tall.
