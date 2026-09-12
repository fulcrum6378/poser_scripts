import poser

from character_dossier import load_dossier
from v4_material_loader import inject_material

choices = set()
scene = poser.Scene()
for mat in scene.CurrentFigure().Materials():
    choices = inject_material(mat, load_dossier()['Shaders'], choices)
scene.Draw()
