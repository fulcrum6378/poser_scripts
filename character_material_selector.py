import poser

import v4_material_loader
from character_dossier import load_dossier

import importlib
importlib.reload(v4_material_loader)

choices = set()
scene = poser.Scene()
figure_name = scene.CurrentFigure().Name()
shaders = load_dossier(figure_name, None, None)['Shaders']
for mat in scene.CurrentFigure().Materials():
    choices = v4_material_loader.inject_material(mat, shaders, choices)
scene.Draw()
