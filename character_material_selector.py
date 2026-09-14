import poser

from character_dossier import load_dossier
from v4_material_loader import inject_material

# import importlib
# importlib.reload(v4_material_loader)

choices = set()
scene = poser.Scene()
figure_name = scene.CurrentFigure().Name()
shaders = load_dossier(figure_name, None, None)['Shaders']
for mat in scene.CurrentFigure().Materials():
    choices = inject_material(mat, shaders, choices)
scene.Draw()
