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
    tree = mat.ShaderTree()
    if mat.Name() == '1_Eyebrow':
        previous_nodes = tree.Nodes()
        root = tree.CreateNode('PhysicalSurface')
        for previous_node in previous_nodes:
            tree.DeleteNode(previous_node)

        root.SetName('PhysicalSurface')
        root.SetLocation(20, 20)
        root.InputByInternalName('Color').SetColor(1, 1, 1)
        root.InputByInternalName('Roughness').SetFloat(0)
        root.InputByInternalName('Specular').SetColor(0, 0, 0)
        root.InputByInternalName('Emission').SetColor(0, 0, 0)
        root.InputByInternalName('SSSMethod').SetFloat(1)
        print(dir(root.InputByInternalName('SSSMethod')))
        # print(dir(root))
        for inp in root.Inputs():
            print(inp.InternalName())
        break
